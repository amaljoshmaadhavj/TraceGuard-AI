"""
Document builder for creating investigation documents from evidence.

Converts raw forensic events into narrative documents designed for
embedding and retrieval in RAG systems.
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DocumentBuilder:
    """
    Converts forensic evidence into investigation documents.
    
    Creates narrative text documents from parsed events that are suitable
    for embedding and retrieval during investigative analysis.
    """
    
    # MITRE ATT&CK technique references by event type
    MITRE_MAPPING = {
        'credential_access': {
            4663: 'T1003 - OS Credential Dumping',
            4656: 'T1003 - OS Credential Dumping',
            4659: 'T1556 - Modify Authentication Process',
            4720: 'T1136 - Create Account',
        },
        'execution': {
            1: 'T1059 - Command and Scripting Interpreter',
            3: 'T1021 - Remote Services',
            11: 'T1566 - Phishing',
        },
        'lateral_movement': {
            4624: 'T1078 - Valid Accounts',
            4648: 'T1570 - Lateral Tool Transfer',
            5145: 'T1021 - Remote Services',
        },
    }
    
    @staticmethod
    def build_event_document(event: Dict) -> str:
        """
        Convert a single event into a narrative document.
        
        Args:
            event: Event dictionary (EventLogEntry or NetworkPacket)
            
        Returns:
            Narrative text document string
        """
        # Check if it's a network packet or event log
        if 'src_ip' in event:
            return DocumentBuilder._build_network_document(event)
        else:
            return DocumentBuilder._build_event_document(event)
    
    @staticmethod
    def _build_event_document(event: Dict) -> str:
        """Build a document from an EventLogEntry."""
        event_id = event.get('event_id', 'Unknown')
        timestamp = event.get('timestamp', 'Unknown')
        user = event.get('user', 'Unknown')
        computer = event.get('computer', 'Unknown')
        process = event.get('process_name', 'Unknown')
        description = event.get('description', 'No description')
        category = event.get('category', 'unknown')
        severity = event.get('severity', 'info')
        
        # Build narrative
        doc = f"""[{category.upper()}] Security Event #{event_id}

TIMESTAMP: {timestamp}
SEVERITY: {severity.upper()}
AFFECTED_SYSTEM: {computer}
USER: {user}

PROCESS_INFORMATION:
  Executable: {process}

EVENT_DETAILS:
{description}

INVESTIGATION_CONTEXT:
This event falls under the '{category}' security category and indicates potential
attack activity during the {category.replace('_', ' ')} phase of a cyber attack.
"""
        
        # Add MITRE mapping if available
        mitre_tech = DocumentBuilder._get_mitre_technique(event_id, category)
        if mitre_tech:
            doc += f"\nMITRE_ATT&CK: {mitre_tech}"
        
        return doc
    
    @staticmethod
    def _build_network_document(packet: Dict) -> str:
        """Build a document from a NetworkPacket."""
        timestamp = packet.get('timestamp', 'Unknown')
        src_ip = packet.get('src_ip', 'Unknown')
        dst_ip = packet.get('dst_ip', 'Unknown')
        src_port = packet.get('src_port', 'N/A')
        dst_port = packet.get('dst_port', 'N/A')
        protocol = packet.get('protocol', 'Unknown')
        packet_size = packet.get('packet_size', 0)
        flags = packet.get('flags', 'None')
        
        # Check for suspicious ports
        suspicious = DocumentBuilder._is_suspicious_network(src_ip, dst_ip, dst_port, protocol)
        severity = 'HIGH' if suspicious else 'MEDIUM'
        
        doc = f"""[NETWORK_COMMUNICATION] {protocol.upper()} Connection

TIMESTAMP: {timestamp}
SEVERITY: {severity}

SOURCE: {src_ip}:{src_port}
DESTINATION: {dst_ip}:{dst_port}

TRAFFIC_DETAILS:
  Protocol: {protocol}
  Packet Size: {packet_size} bytes
  TCP Flags: {flags}
  
INVESTIGATION_CONTEXT:
Network communication detected between internal and external systems.
"""
        
        if suspicious:
            doc += "\nSUSPICIOUS_INDICATORS:\n"
            if dst_port and int(dst_port) in [135, 139, 445, 3389, 5985, 5986]:
                doc += f"  - Destination port {dst_port} commonly associated with lateral movement (RPC/SMB/RDP/WinRM)\n"
        
        return doc
    
    @staticmethod
    def build_investigation_documents(evidence: Dict[str, List[Dict]]) -> List[str]:
        """
        Convert all evidence into investigation documents.
        
        Args:
            evidence: Dictionary of events by category
            
        Returns:
            List of narrative document strings
        """
        documents = []
        
        for category, events in evidence.items():
            logger.info(f"Building documents from {len(events)} events in category '{category}'")
            
            for event in events:
                try:
                    doc = DocumentBuilder.build_event_document(event)
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    logger.error(f"Failed to build document from event: {e}")
        
        logger.info(f"Built {len(documents)} investigation documents")
        return documents
    
    @staticmethod
    def correlate_events_by_timewindow(events: List[Dict], window_minutes: int = 5) -> List[Tuple[str, List[Dict]]]:
        """
        Group events by time window for attack timeline analysis.
        
        Args:
            events: List of events with timestamps
            window_minutes: Time window in minutes
            
        Returns:
            List of (window_label, events) tuples
        """
        if not events:
            return []
        
        # Sort by timestamp
        try:
            sorted_events = sorted(events, key=lambda e: e.get('timestamp', datetime.utcnow()))
        except (TypeError, AttributeError):
            return [(str(datetime.utcnow()), events)]
        
        windows = []
        current_window = None
        current_events = []
        
        for event in sorted_events:
            timestamp = event.get('timestamp')
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except:
                    timestamp = datetime.utcnow()
            
            if current_window is None:
                current_window = timestamp
            
            # Check if event is within current window
            if timestamp - current_window < timedelta(minutes=window_minutes):
                current_events.append(event)
            else:
                # Start new window
                if current_events:
                    windows.append((current_window.isoformat(), current_events))
                current_window = timestamp
                current_events = [event]
        
        # Add final window
        if current_events:
            windows.append((current_window.isoformat(), current_events))
        
        logger.info(f"Correlated {len(events)} events into {len(windows)} time windows")
        return windows
    
    @staticmethod
    def build_timeline_document(windows: List[Tuple[str, List[Dict]]]) -> str:
        """
        Build an attack timeline document from time-correlated events.
        
        Args:
            windows: List of (timestamp_label, events) tuples
            
        Returns:
            Timeline narrative document
        """
        doc = """ATTACK TIMELINE ANALYSIS

Based on forensic evidence, the following attack phases were identified:

"""
        for i, (timestamp, events) in enumerate(windows, 1):
            doc += f"\n--- PHASE {i}: {timestamp} ---\n"
            doc += f"Events in this phase: {len(events)}\n"
            
            # Summarize events
            categories = {}
            for event in events:
                cat = event.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            for cat, count in categories.items():
                doc += f"  - {cat}: {count} events\n"
        
        return doc
    
    @staticmethod
    def _get_mitre_technique(event_id: int, category: str) -> str:
        """
        Look up MITRE ATT&CK technique for an event.
        
        Args:
            event_id: Windows Event ID
            category: Event category
            
        Returns:
            MITRE technique string or empty
        """
        if category in DocumentBuilder.MITRE_MAPPING:
            return DocumentBuilder.MITRE_MAPPING[category].get(event_id, '')
        return ''
    
    @staticmethod
    def _is_suspicious_network(src_ip: str, dst_ip: str, dst_port, protocol: str) -> bool:
        """
        Determine if network communication is suspicious.
        
        Args:
            src_ip: Source IP
            dst_ip: Destination IP
            dst_port: Destination port
            protocol: Protocol (tcp/udp)
            
        Returns:
            True if suspicious
        """
        # Check for suspicious ports
        suspicious_ports = [135, 139, 445, 3389, 5985, 5986]  # RPC, SMB, RDP, WinRM
        try:
            if dst_port and int(dst_port) in suspicious_ports:
                return True
        except (ValueError, TypeError):
            pass
        
        # Check for private -> external (potential exfiltration)
        try:
            if dst_ip and not dst_ip.startswith(('10.', '172.', '192.168.')):
                return True
        except:
            pass
        
        return False
