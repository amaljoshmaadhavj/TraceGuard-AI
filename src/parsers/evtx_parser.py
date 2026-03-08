"""
Windows Event Log (EVTX) parser.

Extracts forensic events from .evtx files with proper error handling
and category mapping to MITRE ATT&CK phases.
"""

import os
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict
from datetime import datetime
import logging

try:
    from Evtx.Evtx import Evtx
except ImportError:
    Evtx = None

from .models import EventLogEntry, SecurityCategory, SeverityLevel, EvidenceMetadata, ParsingResult


logger = logging.getLogger(__name__)


# Event ID to Security Category mapping
EVENT_ID_MAPPING = {
    # Credential Access
    4663: SecurityCategory.CREDENTIAL_ACCESS,  # LSASS access
    4656: SecurityCategory.CREDENTIAL_ACCESS,  # Handle to object requested
    5145: SecurityCategory.LATERAL_MOVEMENT,   # Network share access
    4648: SecurityCategory.LATERAL_MOVEMENT,   # Logon with explicit credentials
    4720: SecurityCategory.CREDENTIAL_ACCESS,  # User account created
    4722: SecurityCategory.CREDENTIAL_ACCESS,  # User account enabled
    
    # Execution
    1: SecurityCategory.EXECUTION,             # Sysmon: Process creation
    3: SecurityCategory.EXECUTION,             # Sysmon: Network connection
    11: SecurityCategory.EXECUTION,            # Sysmon: FileCreate
    
    # Lateral Movement
    4624: SecurityCategory.LATERAL_MOVEMENT,   # Successful logon
    4625: SecurityCategory.LATERAL_MOVEMENT,   # Failed logon
    4720: SecurityCategory.LATERAL_MOVEMENT,   # Account creation
    
    # Persistence
    4688: SecurityCategory.PERSISTENCE,        # Process creation
    
    # Defense Evasion
    4719: SecurityCategory.DEFENSE_EVASION,    # System audit policy change
}

# Event ID to Severity mapping
SEVERITY_MAPPING = {
    4663: SeverityLevel.HIGH,     # LSASS access - critical
    4656: SeverityLevel.MEDIUM,   # Handle to object
    4648: SeverityLevel.HIGH,     # Explicit logon - lateral movement indicator
    5145: SeverityLevel.HIGH,     # Network share
    1: SeverityLevel.MEDIUM,      # Process creation - context dependent
    4688: SeverityLevel.MEDIUM,   # Process creation
}


def extract_text_from_event_xml(event_element: ET.Element) -> Dict[str, str]:
    """
    Extract text content from Event XML element.
    
    Args:
        event_element: ElementTree.Element representing <Event> in EVTX
        
    Returns:
        Dictionary with common Windows Event Log fields
    """
    data = {
        'EventID': None,
        'ComputerName': None,
        'TimeCreated': None,
        'User': None,
        'ProcessName': None,
        'Description': None,
    }
    
    try:
        # Navigate XML structure for common fields
        system = event_element.find('.//System')
        if system is not None:
            # EventID
            event_id_elem = system.find('EventID')
            if event_id_elem is not None:
                data['EventID'] = event_id_elem.text
            
            # Computer name
            computer = system.find('Computer')
            if computer is not None:
                data['ComputerName'] = computer.text
            
            # Timestamp
            time_created = system.find('TimeCreated')
            if time_created is not None:
                data['TimeCreated'] = time_created.get('SystemTime')
            
            # UserID/SID
            security = system.find('Security')
            if security is not None:
                user_id = security.get('UserID')
                if user_id:
                    data['User'] = user_id
        
        # Event data fields
        event_data = event_element.find('.//EventData')
        if event_data is not None:
            for data_elem in event_data.findall('Data'):
                name = data_elem.get('Name', '')
                text = data_elem.text or ''
                
                # Look for process/image name
                if 'Image' in name or 'ProcessName' in name:
                    data['ProcessName'] = text
                
                # Collect all data fields for description
                if text:
                    if 'Description' not in data or data['Description'] is None:
                        data['Description'] = ''
                    data['Description'] += f"{name}: {text}\n"
    
    except Exception as e:
        logger.debug(f"Error extracting text from event XML: {e}")
    
    return data


def parse_timestamp(timestamp_str: Optional[str]) -> Optional[datetime]:
    """
    Parse Windows event timestamp string.
    
    Args:
        timestamp_str: Timestamp in format '2024-01-15T10:23:45.123Z'
        
    Returns:
        datetime object (UTC) or None if parsing fails
    """
    if not timestamp_str:
        return None
    
    try:
        # Handle Sysmon/Windows format: 2024-01-15T10:23:45.123Z
        if 'T' in timestamp_str:
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1]  # Remove Z
            return datetime.fromisoformat(timestamp_str)
        
        # Fallback: Try common formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
    except Exception as e:
        logger.debug(f"Error parsing timestamp '{timestamp_str}': {e}")
    
    return None


class EVTXParser:
    """
    Parser for Windows Event Log (.evtx) files.
    
    Extracts forensic events with proper error handling and security category mapping.
    """
    
    def __init__(self):
        """Initialize EVTX parser."""
        if Evtx is None:
            raise ImportError("python-evtx not installed. Install with: pip install python-evtx")
    
    def parse_event_log(self, file_path: str) -> ParsingResult:
        """
        Parse a single EVTX file.
        
        Args:
            file_path: Path to .evtx file
            
        Returns:
            ParsingResult containing metadata and EventLogEntry list
        """
        result = ParsingResult(
            metadata=EvidenceMetadata(
                file_path=file_path,
                source_type="evtx",
                file_size=os.path.getsize(file_path),
                parse_timestamp=datetime.utcnow(),
                total_events=0,
                success=True
            ),
            events=[]
        )
        
        events: List[EventLogEntry] = []
        errors: List[str] = []
        timestamps: List[Optional[datetime]] = []
        
        try:
            with Evtx(file_path) as log:
                for record in log.records():  # Changed from log.records to log.records()
                    try:
                        event = self._parse_single_event(record)
                        if event:
                            events.append(event)
                            if event.timestamp:
                                timestamps.append(event.timestamp)
                    except Exception as e:
                        error_msg = f"Record {len(events)}: {str(e)}"
                        errors.append(error_msg)
                        logger.debug(error_msg)
                        result.metadata.parse_errors += 1
        
        except Exception as e:
            error_msg = f"Error opening EVTX file: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            result.metadata.success = False
        
        # Update metadata
        result.metadata.total_events = len(events)
        result.metadata.error_details = errors
        
        if timestamps:
            result.metadata.date_range_start = min(timestamps)
            result.metadata.date_range_end = max(timestamps)
        
        # Convert to dict for serialization
        result.events = [event.model_dump() for event in events]
        
        logger.info(f"Parsed {file_path}: {len(events)} events, {result.metadata.parse_errors} errors")
        return result
    
    def _parse_single_event(self, record) -> Optional[EventLogEntry]:
        """
        Parse a single event record from EVTX.
        
        Args:
            record: Event record from python-evtx
            
        Returns:
            EventLogEntry or None if parsing fails
        """
        try:
            # Get XML from record
            event_xml = record.xml()
            root = ET.fromstring(event_xml)
            
            # Extract structured data
            data = extract_text_from_event_xml(root)
            
            event_id = int(data.get('EventID') or 0)
            timestamp = parse_timestamp(data.get('TimeCreated'))
            
            if not timestamp:
                timestamp = datetime.utcnow()
            
            # Map to security category and severity
            category = EVENT_ID_MAPPING.get(event_id, SecurityCategory.UNKNOWN)
            severity = SEVERITY_MAPPING.get(event_id, SeverityLevel.INFO)
            
            return EventLogEntry(
                event_id=event_id,
                timestamp=timestamp,
                source=data.get('ComputerName') or 'Unknown',
                user=data.get('User') or 'Unknown',
                computer=data.get('ComputerName') or 'Unknown',
                process_name=data.get('ProcessName'),
                description=data.get('Description') or f"Event {event_id}",
                category=category,
                severity=severity,
                raw_xml=event_xml
            )
        
        except Exception as e:
            logger.debug(f"Failed to parse event record: {e}")
            return None
    
    def parse_multiple(self, file_paths: List[str]) -> Dict[str, ParsingResult]:
        """
        Parse multiple EVTX files.
        
        Args:
            file_paths: List of .evtx file paths
            
        Returns:
            Dictionary mapping file paths to ParsingResult objects
        """
        results = {}
        for file_path in file_paths:
            try:
                results[file_path] = self.parse_event_log(file_path)
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")
                results[file_path] = ParsingResult(
                    metadata=EvidenceMetadata(
                        file_path=file_path,
                        source_type="evtx",
                        file_size=0,
                        parse_timestamp=datetime.utcnow(),
                        total_events=0,
                        success=False,
                        error_details=[str(e)]
                    ),
                    events=[]
                )
        
        return results
