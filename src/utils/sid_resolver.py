"""
Windows SID (Security Identifier) resolution utilities.

Resolves SIDs to usernames, especially for well-known SIDs.
"""

import re
import logging

logger = logging.getLogger(__name__)


# Well-known Windows SIDs mapping
WELL_KNOWN_SIDS = {
    'S-1-0-0': 'Null',
    'S-1-1-0': 'Everyone',
    'S-1-2-0': 'Local',
    'S-1-3-0': 'Creator Owner',
    'S-1-3-1': 'Creator Group',
    'S-1-5-1': 'Dialup',
    'S-1-5-2': 'Network',
    'S-1-5-3': 'Batch',
    'S-1-5-4': 'Interactive',
    'S-1-5-6': 'Service',
    'S-1-5-7': 'Anonymous',
    'S-1-5-8': 'Proxy',
    'S-1-5-9': 'Enterprise Domain Controllers',
    'S-1-5-10': 'Principal Self',
    'S-1-5-11': 'Authenticated Users',
    'S-1-5-12': 'Restricted Code',
    'S-1-5-13': 'Terminal Server Users',
    'S-1-5-14': 'Remote Interactive Logon',
    'S-1-5-15': 'This Organization',
    'S-1-5-17': 'This Organization',
    'S-1-5-18': 'SYSTEM',
    'S-1-5-19': 'NT AUTHORITY\\LocalService',
    'S-1-5-20': 'NT AUTHORITY\\NetworkService',
    'S-1-5-21-0-0-0-496': 'Compounded Authentication',
    'S-1-5-21-0-0-0-497': 'Claims Valid',
    'S-1-5-32-544': 'BUILTIN\\Administrators',
    'S-1-5-32-545': 'BUILTIN\\Users',
    'S-1-5-32-546': 'BUILTIN\\Guests',
    'S-1-5-32-547': 'BUILTIN\\Power Users',
    'S-1-5-32-548': 'BUILTIN\\Account Operators',
    'S-1-5-32-549': 'BUILTIN\\Server Operators',
    'S-1-5-32-550': 'BUILTIN\\Print Operators',
    'S-1-5-32-551': 'BUILTIN\\Backup Operators',
    'S-1-5-32-552': 'BUILTIN\\Replicators',
    'S-1-5-64-10': 'NTLM Authentication',
    'S-1-5-64-14': 'SChannel Authentication',
    'S-1-5-80-0': 'NT SERVICE',
    'S-1-16-0': 'Untrusted Mandatory Level',
    'S-1-16-4096': 'Low Mandatory Level',
    'S-1-16-8192': 'Medium Mandatory Level',
    'S-1-16-12288': 'High Mandatory Level',
    'S-1-16-16384': 'System Mandatory Level',
}


class SIDResolver:
    """Resolves Windows Security Identifiers (SIDs) to human-readable names."""
    
    # Cache for resolved SIDs to avoid repeated lookups
    _cache = {}
    
    @staticmethod
    def resolve(sid: str) -> str:
        """
        Resolve a SID to a username or description.
        
        Args:
            sid: SID string (e.g., 'S-1-5-21-xxx-xxx-xxx-1000')
            
        Returns:
            Human-readable name or original SID if resolution fails
        """
        if not sid:
            return 'Unknown'
        
        sid = sid.strip()
        
        # Check cache first
        if sid in SIDResolver._cache:
            return SIDResolver._cache[sid]
        
        # Try exact match
        if sid in WELL_KNOWN_SIDS:
            resolved = WELL_KNOWN_SIDS[sid]
            SIDResolver._cache[sid] = resolved
            return resolved
        
        # Try to parse domain/local SID
        resolved = SIDResolver._resolve_domain_sid(sid)
        if resolved != sid:
            SIDResolver._cache[sid] = resolved
            return resolved
        
        # If no resolution, return original
        SIDResolver._cache[sid] = sid
        return sid
    
    @staticmethod
    def _resolve_domain_sid(sid: str) -> str:
        """
        Attempt to parse and interpret domain/local SIDs.
        
        Args:
            sid: SID string
            
        Returns:
            Resolved name or original SID
        """
        try:
            # Pattern: S-1-5-21-X-Y-Z-RID
            # X-Y-Z = domain SID, RID = relative identifier (user/group)
            parts = sid.split('-')
            
            if len(parts) >= 8 and parts[0] == 'S' and parts[2] == '5' and parts[3] == '21':
                # This is a domain SID
                rid = int(parts[-1])
                domain_sid = '-'.join(parts[:-1])
                
                # Interpret RID
                return SIDResolver._interpret_rid(rid, domain_sid)
            
            return sid
        
        except (ValueError, IndexError):
            return sid
    
    @staticmethod
    def _interpret_rid(rid: int, domain_sid: str) -> str:
        """
        Interpret a Relative Identifier (RID) for a user/group.
        
        Args:
            rid: RID value
            domain_sid: Domain SID part
            
        Returns:
            Interpreted name
        """
        # Well-known RID ranges
        if rid == 500:
            return 'Administrator'
        elif rid == 501:
            return 'Guest'
        elif rid == 502:
            return 'KRBTGT'
        elif rid == 512:
            return 'Domain Admins'
        elif rid == 513:
            return 'Domain Users'
        elif rid == 514:
            return 'Domain Guests'
        elif rid == 519:
            return 'Enterprise Admins'
        elif rid == 520:
            return 'Group Policy Creator Owners'
        elif rid == 544:
            return 'Administrators'
        elif rid == 1000:
            return 'Local User'
        elif 1000 <= rid < 10000:
            # Regular user RID
            return f'Domain User (RID: {rid})'
        else:
            return f'User/Group (RID: {rid})'
    
    @staticmethod
    def is_system_account(username_or_sid: str) -> bool:
        """
        Check if account is a system account.
        
        Args:
            username_or_sid: Username or SID string
            
        Returns:
            True if system/service account
        """
        system_accounts = [
            'SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE',
            'S-1-5-18', 'S-1-5-19', 'S-1-5-20',
            'NT AUTHORITY', 'BUILTIN'
        ]
        
        check_val = (username_or_sid or '').upper()
        return any(sys_acc in check_val for sys_acc in system_accounts)
    
    @staticmethod
    def is_admin(username_or_sid: str) -> bool:
        """
        Check if account is an administrator.
        
        Args:
            username_or_sid: Username or SID string
            
        Returns:
            True if admin account
        """
        admin_keywords = [
            'ADMINISTRATOR', 'ADMIN',
            'S-1-5-32-544',  # Administrators group
            'S-1-5-21-.*-512',  # Domain Admins
            'ENTERPRISE ADMIN', 'DOMAIN ADMIN'
        ]
        
        check_val = (username_or_sid or '').upper()
        
        # Exact matches
        if 'ADMINISTRATOR' in check_val:
            return True
        
        # SID pattern match
        for pattern in admin_keywords[2:]:
            if re.search(pattern, check_val):
                return True
        
        return False
