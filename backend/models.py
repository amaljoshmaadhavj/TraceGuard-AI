"""
Pydantic models for API requests/responses
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class FileInfo(BaseModel):
    """File information model"""
    id: str
    filename: str
    category: str
    file_type: str
    size: int
    upload_date: str
    status: str
    events_count: int = 0


class UploadResponse(BaseModel):
    """File upload response"""
    success: bool
    message: str
    file_id: str
    filename: str
    category: str


class QueryRequest(BaseModel):
    """Investigation query request"""
    query: str
    top_k: int = 5


class EvidenceItem(BaseModel):
    """Retrieved evidence item"""
    id: str
    content: str
    similarity: float
    category: str
    severity: str
    timestamp: str


class QueryResponse(BaseModel):
    """Investigation query response"""
    query: str
    response: str
    evidence: List[EvidenceItem]
    confidence: float
    techniques: List[str]
    response_time: float
    evidence_count: int


class StatsData(BaseModel):
    """Statistics data model"""
    total_events: int
    total_files: int
    total_techniques: int
    events_by_category: Dict[str, int]
    severity_distribution: Dict[str, int]
    techniques_list: List[str]


class ProcessingStatus(BaseModel):
    """Processing status model"""
    stage: int
    stage_name: str
    progress: int
    status: str
    message: str


class SettingsModel(BaseModel):
    """Settings model"""
    ollama_endpoint: str
    llm_model: str
    embedding_model: str
    top_k: int
    temperature: float
    data_dir: str
    vectordb_dir: str
