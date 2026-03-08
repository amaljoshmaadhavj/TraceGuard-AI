"""
Investigation analyzer for cyber forensic analysis.

Wraps RAG pipeline with additional analysis features like
MITRE ATT&CK technique mapping and confidence scoring.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
import logging

from ..rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)


@dataclass
class InvestigationResult:
    """Result from investigation analysis."""
    query: str
    response: str
    confidence: float = 1.0
    evidence_count: int = 0
    techniques: List[str] = None
    
    def __post_init__(self):
        if self.techniques is None:
            self.techniques = []


class InvestigationAnalyzer:
    """
    High-level investigation analyzer.
    
    Provides unified interface for querying the investigation system
    with additional analysis features like technique mapping and
    confidence scoring.
    """
    
    def __init__(self, 
                 vectordb_dir: str = "./vectordb",
                 ollama_url: str = "http://localhost:11434"):
        """
        Initialize analyzer.
        
        Args:
            vectordb_dir: FAISS vector DB directory
            ollama_url: Ollama service endpoint
        """
        self.pipeline = RAGPipeline(
            vectordb_dir=vectordb_dir,
            ollama_url=ollama_url,
            top_k=5
        )
    
    def analyze(self, query: str) -> InvestigationResult:
        """
        Analyze investigator query.
        
        Args:
            query: Investigator question
            
        Returns:
            InvestigationResult with response and metadata
        """
        # Normalize query
        normalized_query = self._normalize_query(query)
        
        logger.info(f"Analyzing: {normalized_query}")
        
        if not self.pipeline.is_ready():
            return InvestigationResult(
                query=query,
                response="System not ready. Ensure vector database and Ollama are configured.",
                confidence=0.0
            )
        
        # Get evidence for analysis
        evidence = self.pipeline.debug_evidence(normalized_query)
        
        # Generate response
        response = self.pipeline.answer_query(normalized_query)
        
        # Extract techniques from evidence and response
        techniques = self._extract_techniques(evidence, response)
        
        return InvestigationResult(
            query=query,
            response=response,
            confidence=self._calculate_confidence(evidence),
            evidence_count=len(evidence),
            techniques=techniques
        )
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize investigator query.
        
        Args:
            query: Raw query string
            
        Returns:
            Normalized query
        """
        # Expand common abbreviations
        replacements = {
            'LSASS': 'Local Authority Subsystem Service credential dumping',
            'SMB': 'Server Message Block network sharing',
            'RDP': 'Remote Desktop Protocol',
            'WMI': 'Windows Management Instrumentation',
            'UAC': 'User Account Control bypass',
            'ACE': 'Access Control Entry',
            'SID': 'Security Identifier',
            'GUID': 'Globally Unique Identifier',
        }
        
        normalized = query
        for abbrev, expansion in replacements.items():
            if abbrev in query.upper():
                normalized = normalized.replace(abbrev, expansion)
        
        return normalized
    
    def _extract_techniques(self, evidence: List[Dict], response: str) -> List[str]:
        """
        Extract MITRE ATT&CK techniques from evidence and response.
        
        Args:
            evidence: Retrieved evidence list
            response: LLM response
            
        Returns:
            List of technique IDs (T#### format)
        """
        techniques = set()
        
        # Look for T#### pattern in response
        import re
        pattern = r'T\d{4}'
        technique_matches = re.findall(pattern, response)
        techniques.update(technique_matches)
        
        # Check metadata for techniques
        for item in evidence:
            metadata = item.get('metadata', {})
            if 'technique' in metadata:
                techniques.add(metadata['technique'])
        
        return sorted(list(techniques))
    
    def _calculate_confidence(self, evidence: List[Dict]) -> float:
        """
        Calculate confidence score based on evidence quality.
        
        Args:
            evidence: Retrieved evidence list
            
        Returns:
            Confidence score 0-1
        """
        if not evidence:
            return 0.0
        
        # Average similarity score
        similarities = [
            item.get('similarity', 0.0) for item in evidence
        ]
        
        if similarities:
            avg_similarity = sum(similarities) / len(similarities)
            return min(1.0, avg_similarity * 1.2)  # Slight boost
        
        return 0.5
    
    def suggest_queries(self) -> List[str]:
        """
        Suggest example queries for investigators.
        
        Returns:
            List of example queries
        """
        return [
            "What credential access attempts were detected?",
            "Was there evidence of credential dumping attacks?",
            "Show me the execution process timeline",
            "What lateral movement activity occurred?",
            "Which processes exhibit suspicious behavior?",
            "Are there signs of persistence mechanisms?",
            "What external communications were made?",
            "Summarize the complete attack timeline",
        ]
