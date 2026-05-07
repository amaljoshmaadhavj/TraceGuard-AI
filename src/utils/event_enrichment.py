"""
Windows Event enrichment and interpretation.

Provides human-readable interpretations of Windows event IDs,
templates for common security events, and attack significance assessment.
"""

import logging
from typing import Dict, Optional
from .sid_resolver import SIDResolver

logger = logging.getLogger(__name__)


class WindowsEventInterpreter:
    """Interprets Windows security events with rich descriptions."""
    
    # Event ID to description mapping
    EVENT_DESCRIPTIONS = {
        # Credential Access Events
        4663: {
            'name': 'Attempt to Access LSASS Process',
            'category': 'credential_access',
            'severity': 'CRITICAL',
            'template': 'Process {process_name} (PID: {process_id}) by {user} on {computer} attempted to access LSASS (Local Authority Subsystem Service). This indicates potential credential dumping attack.',
            'mitre_technique': 'T1003 - OS Credential Dumping',
            'attack_phase': 'Credential Access'
        },
        4656: {
            'name': 'Handle Requested to Object',
            'category': 'credential_access',
            'severity': 'HIGH',
            'template': '{user} on {computer} requested a handle to {object_name} with access mask {access_mask}. May indicate privilege escalation or lateral movement attempt.',
            'mitre_technique': 'T1003 - OS Credential Dumping',
            'attack_phase': 'Credential Access'
        },
        4720: {
            'name': 'User Account Created',
            'category': 'persistence',
            'severity': 'HIGH',
            'template': 'New user account {target_user_name} was created on {computer} by {user}. Attacker may be establishing persistence through backdoor account creation.',
            'mitre_technique': 'T1136 - Create Account',
            'attack_phase': 'Persistence'
        },
        4722: {
            'name': 'User Account Enabled',
            'category': 'persistence',
            'severity': 'MEDIUM',
            'template': 'User account {target_user_name} was re-enabled on {computer} by {user}. May indicate reactivation of hidden backdoor account.',
            'mitre_technique': 'T1136 - Create Account',
            'attack_phase': 'Persistence'
        },
        
        # Execution Events (Sysmon)
        1: {
            'name': 'Process Creation',
            'category': 'execution',
            'severity': 'MEDIUM',
            'template': 'Process {process_name} (PID: {process_id}) created by {parent_process_name} (PPID: {parent_process_id}) on {computer}. Command: {command_line}',
            'mitre_technique': 'T1059 - Command and Scripting Interpreter',
            'attack_phase': 'Execution'
        },
        3: {
            'name': 'Network Connection',
            'category': 'execution',
            'severity': 'MEDIUM',
            'template': 'Process {process_name} (PID: {process_id}) on {computer} initiated network connection to {destination_ip}:{destination_port} ({protocol}). Source port: {source_port}',
            'mitre_technique': 'T1571 - Non-Standard Port',
            'attack_phase': 'Command & Control'
        },
        11: {
            'name': 'File Created',
            'category': 'execution',
            'severity': 'LOW',
            'template': 'Process {process_name} (PID: {process_id}) created file {target_filename} on {computer}',
            'mitre_technique': 'T1566 - Phishing',
            'attack_phase': 'Initial Access'
        },
        
        # Lateral Movement Events
        4624: {
            'name': 'Successful Logon',
            'category': 'lateral_movement',
            'severity': 'MEDIUM',
            'template': '{user} successfully logged on to {computer} from {source_network_address}. Logon type: {logon_type_name}. This could indicate lateral movement if unusual logon type or source.',
            'mitre_technique': 'T1078 - Valid Accounts',
            'attack_phase': 'Lateral Movement'
        },
        4625: {
            'name': 'Failed Logon',
            'category': 'lateral_movement',
            'severity': 'LOW',
            'template': 'Failed logon attempt for {target_user_name} on {computer} from {source_network_address}. Logon type: {logon_type_name}. Failure reason: {failure_reason}',
            'mitre_technique': 'T1110 - Brute Force',
            'attack_phase': 'Initial Access'
        },
        4648: {
            'name': 'Logon with Explicit Credentials',
            'category': 'lateral_movement',
            'severity': 'HIGH',
            'template': '{subject_user_name} on {source_computer} logged in to {target_user_name} account on {computer} using explicit credentials. HIGHLY SUSPICIOUS - indicates lateral movement or credential theft.',
            'mitre_technique': 'T1570 - Lateral Tool Transfer',
            'attack_phase': 'Lateral Movement'
        },
        5145: {
            'name': 'Network Share Access',
            'category': 'lateral_movement',
            'severity': 'HIGH',
            'template': '{subject_user_name} from {source_ip_address} accessed network share \\\\{object_name} on {computer}. Access type: {access_request_type}. May indicate lateral movement via SMB.',
            'mitre_technique': 'T1021 - Remote Services',
            'attack_phase': 'Lateral Movement'
        },
        
        # Defense Evasion
        4719: {
            'name': 'System Audit Policy Changed',
            'category': 'defense_evasion',
            'severity': 'CRITICAL',
            'template': 'System audit policy was changed on {computer}. Subject: {subject_user_name}. CRITICAL: Attacker likely attempting to disable logging/auditing.',
            'mitre_technique': 'T1562 - Impair Defenses',
            'attack_phase': 'Defense Evasion'
        },
        4688: {
            'name': 'Process Creation with Details',
            'category': 'execution',
            'severity': 'MEDIUM',
            'template': 'Process {process_name} (PID: {process_id}) created on {computer} by {creator_user_name}. Parent process: {parent_process_id}. Command line: {process_command_line}',
            'mitre_technique': 'T1059 - Command and Scripting Interpreter',
            'attack_phase': 'Execution'
        },
    }
    
    # Logon type interpretation
    LOGON_TYPES = {
        '2': 'Interactive (User logged in locally)',
        '3': 'Network (Network share access)',
        '4': 'Batch (Scheduled task)',
        '5': 'Service (Service started)',
        '7': 'Unlock (Workstation unlocked)',
        '8': 'NetworkCleartext (Network logon with plaintext password)',
        '9': 'NewCredentials (RunAs with new credentials)',
        '10': 'RemoteInteractive (RDP/Remote Desktop)',
        '11': 'CachedInteractive (Cached credentials)',
    }
    
    # Suspicious process names
    SUSPICIOUS_PROCESSES = {
        'rundll32.exe': 'Living off the land - can execute arbitrary code',
        'regsvcs.exe': 'Living off the land - .NET code execution',
        'regasm.exe': 'Living off the land - .NET code execution',
        'cscript.exe': 'Script execution - common malware vector',
        'wscript.exe': 'Script execution - common malware vector',
        'powershell.exe': 'PowerShell execution - common attack tool',
        'cmd.exe': 'Command shell - common attack tool',
        'certutil.exe': 'Certificate tool - often abused for file download',
        'bitsadmin.exe': 'BITS transfer - often used for data exfiltration',
        'mshta.exe': 'HTML application host - script execution',
        'svchost.exe': 'Service host - should not create child processes',
        'lsass.exe': 'LSASS process - should not create child processes',
        'svchost.exe': 'Service host - suspicious if creating processes',
        'winlogon.exe': 'Windows logon - suspicious if creating processes',
    }
    
    @staticmethod
    def interpret_event(event_id: int, event_data: Dict) -> Dict:
        """
        Interpret a Windows event with rich context.
        
        Args:
            event_id: Windows event ID
            event_data: Event data dictionary
            
        Returns:
            Dictionary with interpretation details
        """
        if event_id not in WindowsEventInterpreter.EVENT_DESCRIPTIONS:
            return {
                'name': f'Windows Event {event_id}',
                'description': f'Uninterpreted Windows Security Event {event_id}',
                'category': 'unknown',
                'severity': 'LOW',
                'mitre_technique': None,
            }
        
        desc = WindowsEventInterpreter.EVENT_DESCRIPTIONS[event_id]
        
        # Resolve SIDs to usernames
        resolved_data = WindowsEventInterpreter._resolve_sids_in_data(event_data)
        
        # Build description from template
        description = desc['template']
        try:
            description = description.format(**resolved_data)
        except (KeyError, ValueError):
            # Fallback if formatting fails
            description = desc['template']
        
        # Check for suspicious processes
        severity = desc['severity']
        process_name = event_data.get('process_name', '').lower()
        if process_name in WindowsEventInterpreter.SUSPICIOUS_PROCESSES:
            severity = 'CRITICAL' if severity != 'CRITICAL' else 'CRITICAL'
        
        return {
            'name': desc['name'],
            'description': description,
            'category': desc['category'],
            'severity': severity,
            'mitre_technique': desc['mitre_technique'],
            'attack_phase': desc.get('attack_phase', 'Unknown'),
        }
    
    @staticmethod
    def _resolve_sids_in_data(event_data: Dict) -> Dict:
        """
        Resolve all SIDs in event data to usernames.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Updated event data with resolved SIDs
        """
        resolved = dict(event_data)
        
        sid_fields = [
            'user', 'subject_user_name', 'target_user_name',
            'source_user_id', 'target_user_id', 'subject_user_id'
        ]
        
        for field in sid_fields:
            if field in resolved and resolved[field]:
                resolved[field] = SIDResolver.resolve(resolved[field])
        
        return resolved
    
    @staticmethod
    def get_logon_type_name(logon_type: str) -> str:
        """
        Get human-readable logon type.
        
        Args:
            logon_type: Logon type number as string
            
        Returns:
            Logon type description
        """
        return WindowsEventInterpreter.LOGON_TYPES.get(
            str(logon_type), 
            f'Logon Type {logon_type}'
        )
    
    @staticmethod
    def is_suspicious_process(process_name: str) -> bool:
        """
        Check if process is suspicious.
        
        Args:
            process_name: Process executable name
            
        Returns:
            True if suspicious
        """
        if not process_name:
            return False
        
        return process_name.lower() in WindowsEventInterpreter.SUSPICIOUS_PROCESSES
    
    @staticmethod
    def get_threat_level(event_id: int) -> str:
        """
        Get threat level for event ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Threat level: CRITICAL, HIGH, MEDIUM, LOW
        """
        if event_id in WindowsEventInterpreter.EVENT_DESCRIPTIONS:
            return WindowsEventInterpreter.EVENT_DESCRIPTIONS[event_id]['severity']
        return 'UNKNOWN'
