"""
MITRE ATT&CK technique mapper.

Maps forensic events to MITRE ATT&CK framework techniques
for comprehensive threat analysis.
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MITREMapper:
    """
    Maps forensic events to MITRE ATT&CK techniques.
    
    Provides lookup and correlation between Windows event IDs,
    network behaviors, and MITRE ATT&CK framework techniques.
    """
    
    # Comprehensive mapping of Windows Event IDs to MITRE techniques
    EVENT_ID_TO_TECHNIQUE = {
        # Credential Access
        4663: {
            'id': 'T1003',
            'name': 'OS Credential Dumping',
            'subtechnique': 'LSASS Memory',
            'description': 'LSASS access attempt detected'
        },
        4656: {
            'id': 'T1003',
            'name': 'OS Credential Dumping',
            'description': 'Handle request to privileged resource'
        },
        4720: {
            'id': 'T1136.001',
            'name': 'Create Account: Local Account',
            'description': 'Local user account creation detected'
        },
        4722: {
            'id': 'T1136.001',
            'name': 'Create Account: Local Account',
            'description': 'Local user account enabled'
        },
        4765: {
            'id': 'T1136.001',
            'name': 'Create Account: Local Account',
            'description': 'SID history added to account'
        },
        
        # Lateral Movement
        4624: {
            'id': 'T1078.001',
            'name': 'Valid Accounts: Default Accounts',
            'description': 'Successful logon detected'
        },
        4625: {
            'id': 'T1110',
            'name': 'Brute Force',
            'description': 'Failed logon attempt'
        },
        4648: {
            'id': 'T1570',
            'name': 'Lateral Tool Transfer',
            'description': 'Logon with explicit credentials'
        },
        5145: {
            'id': 'T1021.002',
            'name': 'Remote Services: SMB/Windows Admin Shares',
            'description': 'Network share object accessed'
        },
        3389: {
            'id': 'T1021.001',
            'name': 'Remote Services: Remote Desktop Protocol',
            'description': 'RDP connection detected'
        },
        
        # Execution
        1: {
            'id': 'T1059.001',
            'name': 'Command and Scripting Interpreter: PowerShell',
            'description': 'Process creation detected (Sysmon)',
            'datasource': 'Sysmon'
        },
        3: {
            'id': 'T1021',
            'name': 'Remote Services',
            'description': 'Network connection detected (Sysmon)',
            'datasource': 'Sysmon'
        },
        11: {
            'id': 'T1566',
            'name': 'Phishing',
            'description': 'File created (Sysmon)',
            'datasource': 'Sysmon'
        },
        
        # Persistence
        4688: {
            'id': 'T1053.005',
            'name': 'Scheduled Task/Job: Scheduled Task',
            'description': 'Process created'
        },
        4698: {
            'id': 'T1053.005',
            'name': 'Scheduled Task/Job: Scheduled Task',
            'description': 'Scheduled task created'
        },
        
        # Defense Evasion
        4719: {
            'id': 'T1562.002',
            'name': 'Impair Defenses: Disable Windows Event Logging',
            'description': 'System audit policy modified'
        },
        4706: {
            'id': 'T1556',
            'name': 'Modify Authentication Process',
            'description': 'Trust relationship modified'
        },
        
        # Discovery
        4688: {
            'id': 'T1087',
            'name': 'Account Discovery',
            'description': 'Administrative commands',
        },
    }
    
    # Network behavior patterns to techniques
    NETWORK_PATTERNS = {
        'C2': {
            'ports': [443, 80, 8080, 8443, 9200],
            'techniques': ['T1071', 'T1095'],  # Application Layer Protocol, Non-Application Layer Protocol
            'description': 'Potential C2 communication'
        },
        'Exfiltration': {
            'ports': [443, 80, 22],
            'techniques': ['T1041'],  # Exfiltration Over C2 Channel
            'description': 'Data exfiltration detected'
        },
        'RDP': {
            'ports': [3389],
            'techniques': ['T1021.001'],  # Remote Desktop Protocol
            'description': 'RDP lateral movement'
        },
        'SMB': {
            'ports': [445, 139, 135],
            'techniques': ['T1021.002'],  # SMB/Windows Admin Shares
            'description': 'SMB lateral movement'
        },
        'WinRM': {
            'ports': [5985, 5986],
            'techniques': ['T1021.006'],  # Windows Remote Management
            'description': 'WinRM lateral movement'
        },
    }
    
    @staticmethod
    def get_technique_for_event(event_id: int) -> Optional[Dict]:
        """
        Get MITRE technique for Windows Event ID.
        
        Args:
            event_id: Windows Event ID
            
        Returns:
            Dictionary with technique info or None
        """
        return MITREMapper.EVENT_ID_TO_TECHNIQUE.get(event_id)
    
    @staticmethod
    def get_all_techniques() -> Dict[int, Dict]:
        """
        Get all event ID to technique mappings.
        
        Returns:
            Complete mapping dictionary
        """
        return MITREMapper.EVENT_ID_TO_TECHNIQUE.copy()
    
    @staticmethod
    def get_techniques_for_events(event_ids: List[int]) -> List[str]:
        """
        Get unique MITRE techniques for a list of event IDs.
        
        Args:
            event_ids: List of Windows Event IDs
            
        Returns:
            List of unique technique IDs (T####)
        """
        techniques_set = set()
        
        for event_id in event_ids:
            technique = MITREMapper.get_technique_for_event(event_id)
            if technique:
                techniques_set.add(technique['id'])
        
        return sorted(list(techniques_set))
    
    @staticmethod
    def get_network_technique(port: int, protocol: str = 'tcp') -> Optional[Dict]:
        """
        Determine MITRE technique for network activity.
        
        Args:
            port: Destination port
            protocol: Protocol (tcp/udp/icmp)
            
        Returns:
            Technique info or None
        """
        for pattern, info in MITREMapper.NETWORK_PATTERNS.items():
            if port in info.get('ports', []):
                return {
                    'pattern': pattern,
                    'techniques': info['techniques'],
                    'description': info['description']
                }
        
        return None
    
    @staticmethod
    def build_technique_report(events: List[Dict]) -> Dict[str, any]:
        """
        Build comprehensive MITRE technique report from events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Report dictionary with techniques and tactics
        """
        report = {
            'total_events': len(events),
            'techniques': {},
            'tactics': set(),
        }
        
        # Map events to techniques
        for event in events:
            event_id = event.get('event_id')
            if event_id:
                technique = MITREMapper.get_technique_for_event(event_id)
                if technique:
                    tech_id = technique['id']
                    if tech_id not in report['techniques']:
                        report['techniques'][tech_id] = {
                            'name': technique.get('name'),
                            'count': 0,
                            'events': []
                        }
                    report['techniques'][tech_id]['count'] += 1
                    report['techniques'][tech_id]['events'].append({
                        'timestamp': event.get('timestamp'),
                        'event_id': event_id,
                        'user': event.get('user'),
                    })
        
        return report
