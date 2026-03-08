"""
Data models for forensic evidence parsing.

Defines Pydantic models for structured representation of Windows Event Log entries from EVTX files.
"""

from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from pydantic import BaseModel, Field


class SecurityCategory(str, Enum):
    """Security event categories mapped to MITRE ATT&CK phases."""
    CREDENTIAL_ACCESS = "credential_access"
    EXECUTION = "execution"
    LATERAL_MOVEMENT = "lateral_movement"
    PERSISTENCE = "persistence"
    DISCOVERY = "discovery"
    COLLECTION = "collection"
    EXFILTRATION = "exfiltration"
    DEFENSE_EVASION = "defense_evasion"
    UNKNOWN = "unknown"


class SeverityLevel(str, Enum):
    """Severity levels for security events."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventLogEntry(BaseModel):
    """
    Represents a single Windows Event Log entry from EVTX file.
    
    Extracted with key forensic attributes for investigation.
    """
    event_id: int = Field(..., description="Windows Event ID")
    timestamp: datetime = Field(..., description="Event timestamp (UTC)")
    source: str = Field(..., description="Event source/provider")
    user: str = Field(..., description="User associated with event (SID or username)")
    computer: str = Field(..., description="Computer/hostname where event occurred")
    process_name: Optional[str] = Field(None, description="Process name/executable")
    process_id: Optional[int] = Field(None, description="Process ID")
    description: str = Field(..., description="Event description/details")
    category: SecurityCategory = Field(default=SecurityCategory.UNKNOWN)
    severity: SeverityLevel = Field(default=SeverityLevel.INFO)
    raw_xml: Optional[str] = Field(None, description="Raw XML event data for detail inspection")
    
    class Config:
        use_enum_values = True


class EvidenceMetadata(BaseModel):
    """
    Metadata for an evidence file.
    
    Tracks parsing results and file-level statistics.
    """
    file_path: str = Field(..., description="Absolute path to evidence file")
    source_type: str = Field(default="evtx", description="Evidence type (evtx)")
    file_size: int = Field(..., description="File size in bytes")
    parse_timestamp: datetime = Field(..., description="When file was parsed")
    total_events: int = Field(..., description="Total events extracted")
    date_range_start: Optional[datetime] = Field(None, description="Earliest event timestamp")
    date_range_end: Optional[datetime] = Field(None, description="Latest event timestamp")
    parse_errors: int = Field(default=0, description="Number of parsing errors encountered")
    error_details: List[str] = Field(default_factory=list, description="Details of parsing errors")
    success: bool = Field(default=True, description="Whether parsing completed successfully")


class ParsingResult(BaseModel):
    """
    Result of parsing a single evidence file.
    
    Contains metadata and extracted events.
    """
    metadata: EvidenceMetadata
    events: List[dict] = Field(default_factory=list, description="List of EventLogEntry dicts")
    
    class Config:
        arbitrary_types_allowed = True


class EvidenceCatalog(BaseModel):
    """
    Complete catalog of all parsed evidence across multiple files.
    
    Aggregates results organized by security category.
    """
    parse_timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_files: int = Field(description="Total evidence files processed")
    total_events: int = Field(description="Total events extracted from all files")
    total_errors: int = Field(description="Total parsing errors across all files")
    
    # Organized by category
    event_logs: Dict[str, List[EventLogEntry]] = Field(default_factory=dict, description="Event logs by security category")
    
    # Metadata tracking
    file_metadata: List[EvidenceMetadata] = Field(default_factory=list, description="Metadata for all processed files")
    
    class Config:
        arbitrary_types_allowed = True
