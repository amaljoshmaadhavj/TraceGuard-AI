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

# Import enrichment utilities
sys_path_added = False
try:
    from ..utils.sid_resolver import SIDResolver
    from ..utils.event_enrichment import WindowsEventInterpreter
except ImportError:
    # Fallback if imports fail
    SIDResolver = None
    WindowsEventInterpreter = None


logger = logging.getLogger(__name__)


# Event ID to Security Category mapping
# Note: Removed duplicates. Each event ID maps to its primary category.
EVENT_ID_MAPPING = {
    # Credential Access
    4663: SecurityCategory.CREDENTIAL_ACCESS,  # LSASS access - credential dumping
    4656: SecurityCategory.CREDENTIAL_ACCESS,  # Handle to object requested
    
    # Persistence
    4720: SecurityCategory.PERSISTENCE,        # User account created - potential backdoor account
    4722: SecurityCategory.PERSISTENCE,        # User account enabled - reactivating hidden account
    
    # Execution (Sysmon events)
    1: SecurityCategory.EXECUTION,             # Sysmon: Process creation
    3: SecurityCategory.EXECUTION,             # Sysmon: Network connection
    11: SecurityCategory.EXECUTION,            # Sysmon: FileCreate
    
    # Lateral Movement
    4624: SecurityCategory.LATERAL_MOVEMENT,   # Successful logon
    4625: SecurityCategory.LATERAL_MOVEMENT,   # Failed logon
    4648: SecurityCategory.LATERAL_MOVEMENT,   # Logon with explicit credentials - lateral movement
    5145: SecurityCategory.LATERAL_MOVEMENT,   # Network share access - lateral movement via SMB
    
    # Defense Evasion
    4688: SecurityCategory.EXECUTION,          # Process creation (with details)
    4719: SecurityCategory.DEFENSE_EVASION,    # System audit policy change
    1102: SecurityCategory.DEFENSE_EVASION,    # The audit log was cleared
    104: SecurityCategory.DEFENSE_EVASION,     # The system log was cleared
}

# Event ID to Severity mapping
SEVERITY_MAPPING = {
    4663: SeverityLevel.HIGH,     # LSASS access - critical
    4656: SeverityLevel.MEDIUM,   # Handle to object
    4648: SeverityLevel.HIGH,     # Explicit logon - lateral movement indicator
    5145: SeverityLevel.HIGH,     # Network share
    1: SeverityLevel.MEDIUM,      # Process creation - context dependent
    4688: SeverityLevel.MEDIUM,   # Process creation
    1102: SeverityLevel.HIGH,     # Audit log cleared - evidence destruction
    104: SeverityLevel.HIGH,      # System log cleared - evidence destruction
}


def extract_text_from_event_xml(event_element: ET.Element) -> Dict[str, str]:
    """
    Extract text content from Event XML element.
    
    Handles Windows Event Log XML with proper namespace support.
    
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
        # Define namespace for Windows Event XML
        ns_uri = '{http://schemas.microsoft.com/win/2004/08/events/event}'
        
        # Find System element (with or without namespace)
        system = event_element.find(f'.//{ns_uri}System')
        if system is None:
            system = event_element.find('.//System')
        
        if system is not None:
            # EventID - it's directly as text, not an attribute
            event_id_elem = system.find(f'{ns_uri}EventID')
            if event_id_elem is None:
                event_id_elem = system.find('EventID')
            
            if event_id_elem is not None and event_id_elem.text:
                data['EventID'] = event_id_elem.text
            
            # Computer name
            computer = system.find(f'{ns_uri}Computer')
            if computer is None:
                computer = system.find('Computer')
            
            if computer is not None and computer.text:
                data['ComputerName'] = computer.text
            
            # Timestamp from SystemTime attribute
            time_created = system.find(f'{ns_uri}TimeCreated')
            if time_created is None:
                time_created = system.find('TimeCreated')
            
            if time_created is not None:
                sys_time = time_created.get('SystemTime')
                if sys_time:
                    data['TimeCreated'] = sys_time
        
        # Event data fields - this is where the real data lives
        event_data = event_element.find(f'.//{ns_uri}EventData')
        if event_data is None:
            event_data = event_element.find('.//EventData')
        
        if event_data is not None:
            description_parts = []
            
            # Extract all Data elements
            data_elems = event_data.findall(f'{ns_uri}Data')
            if not data_elems:
                data_elems = event_data.findall('Data')
            
            for data_elem in data_elems:
                name = data_elem.get('Name', '')
                text = (data_elem.text or '').strip()
                
                if not text:
                    continue
                
                # Extract user information from various possible field names
                if not data['User'] or data['User'] == 'Unknown':
                    if any(x in name for x in ['UserName', 'User', 'TargetUserName', 'SubjectUserName']):
                        data['User'] = text
                
                # Extract domain
                domain = None
                if any(x in name for x in ['DomainName', 'SubjectDomainName', 'TargetDomainName']):
                    domain = text
                
                # Extract process name
                if not data['ProcessName']:
                    if any(x in name for x in ['ProcessName', 'Image', 'ImageName']):
                        data['ProcessName'] = text
                
                # Build description from key fields
                # Only include fields that have meaningful data
                important_fields = [
                    'ProcessName', 'Image', 'ProcessID', 'ParentProcessID',
                    'TargetUserName', 'SubjectUserName', 'SubjectDomainName',
                    'ObjectName', 'CommandLine', 'ParentImage',
                    'SourceIp', 'DestinationIp', 'DestinationPort',
                    'AccessList', 'PrivilegeList', 'AccessMask'
                ]
                
                # Include important fields in description
                if any(field in name for field in important_fields):
                    # Truncate very long fields
                    truncated = text[:200] if len(text) > 200 else text
                    description_parts.append(f"{name}: {truncated}")
            
            # Create description from important fields
            if description_parts:
                data['Description'] = '\n'.join(description_parts)
            else:
                # Fallback: include all non-empty fields
                data_elems_fb = event_data.findall(f'{ns_uri}Data')
                if not data_elems_fb:
                    data_elems_fb = event_data.findall('Data')
                data['Description'] = '\n'.join([
                    f"{d.get('Name', '')}: {(d.text or '')[:100]}"
                    for d in data_elems_fb
                    if (d.text or '').strip()
                ])
        
        # Ensure we have some description
        if not data['Description']:
            data['Description'] = f"Event {data.get('EventID', 'Unknown')}"
    
    except Exception as e:
        logger.debug(f"Error extracting text from event XML: {e}")
        data['Description'] = f"Event {data.get('EventID', 'Unknown')}"
    
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
            
            # Resolve SIDs to usernames if possible
            user = data.get('User') or 'Unknown'
            if SIDResolver:
                user = SIDResolver.resolve(user)
            
            # Build enriched description
            description = data.get('Description') or f"Event {event_id}"
            if WindowsEventInterpreter:
                try:
                    interpretation = WindowsEventInterpreter.interpret_event(event_id, data)
                    # Use rich description if available
                    if interpretation.get('description'):
                        description = interpretation['description']
                    # Upgrade severity based on interpretation
                    if interpretation.get('severity'):
                        severity_map = {
                            'CRITICAL': SeverityLevel.CRITICAL,
                            'HIGH': SeverityLevel.HIGH,
                            'MEDIUM': SeverityLevel.MEDIUM,
                            'LOW': SeverityLevel.LOW,
                        }
                        severity = severity_map.get(interpretation['severity'], severity)
                except Exception as e:
                    logger.debug(f"Failed to enrich event {event_id}: {e}")
            
            return EventLogEntry(
                event_id=event_id,
                timestamp=timestamp,
                source=data.get('ComputerName') or 'Unknown',
                user=user,
                computer=data.get('ComputerName') or 'Unknown',
                process_name=data.get('ProcessName'),
                description=description,
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
