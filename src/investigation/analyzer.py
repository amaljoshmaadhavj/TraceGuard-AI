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
            top_k=3
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
        
        Multiple extraction methods for robustness:
        - Regex pattern matching for T#### format
        - Metadata extraction from evidence
        - Technique name pattern matching
        
        Args:
            evidence: Retrieved evidence list
            response: LLM response
            
        Returns:
            List of technique identifiers with full details
        """
        techniques = {}  # Use dict to avoid duplicates while preserving info
        
        # Method 1: Look for T#### pattern in response
        import re
        pattern = r'T\d{4}'
        technique_matches = re.findall(pattern, response)
        for tech in technique_matches:
            if tech not in techniques:
                techniques[tech] = {'id': tech, 'source': 'response'}
        
        # Method 2: Check metadata for techniques
        for item in evidence:
            metadata = item.get('metadata', {})
            
            # Look for 'technique' field in metadata
            if 'technique' in metadata:
                tech = metadata['technique']
                if tech not in techniques:
                    techniques[tech] = {'id': tech, 'source': 'metadata'}
            
            # Look in full metadata dict
            full_meta = metadata.get('metadata', {})
            if isinstance(full_meta, dict) and 'mitre_techniques' in full_meta:
                tech_list = full_meta['mitre_techniques']
                if isinstance(tech_list, list):
                    for tech in tech_list:
                        if tech not in techniques:
                            techniques[tech] = {'id': tech, 'source': 'metadata'}
                elif isinstance(tech_list, str):
                    if tech_list not in techniques:
                        techniques[tech_list] = {'id': tech_list, 'source': 'metadata'}
        
        # Method 3: Try to extract technique descriptions from response
        technique_keywords = {
            'credential dumping': 'T1003',
            'pass the hash': 'T1550',
            'lateral movement': 'T1021',
            'privilege escalation': 'T1548',
            'persistence': 'T1547',
            'defense evasion': 'T1562',
            'command and control': 'T1071',
            'exfiltration': 'T1020',
            'impact': 'T1531',
        }
        
        response_lower = response.lower()
        for keyword, tech_id in technique_keywords.items():
            if keyword in response_lower and tech_id not in techniques:
                techniques[tech_id] = {'id': tech_id, 'source': 'inferred', 'keyword': keyword}
        
        # Return sorted list of technique IDs
        return sorted([t['id'] for t in techniques.values()])
    
    def _calculate_confidence(self, evidence: List[Dict]) -> float:
        """
        Calculate confidence score based on evidence quality.
        
        Multi-factor confidence assessment based on:
        - Number of relevant documents retrieved
        - Similarity scores of retrieved documents
        - Consistency across results
        - Relevance diversity
        
        Args:
            evidence: Retrieved evidence list
            
        Returns:
            Confidence score 0-1
        """
        if not evidence:
            return 0.0
        
        # Factor 1: Evidence count (more is better, diminishing returns)
        evidence_count_factor = min(len(evidence) / 5.0, 1.0)  # Max at 5+ docs
        
        # Factor 2: Similarity scores
        similarities = [
            item.get('similarity', 0.0) for item in evidence
        ]
        
        if not similarities:
            return 0.3  # Minimal confidence if no similarities
        
        avg_similarity = sum(similarities) / len(similarities)
        min_similarity = min(similarities)
        
        # Factor 3: Consistency (do results agree?)
        # Higher std dev = less consistent
        variance = sum((s - avg_similarity) ** 2 for s in similarities) / len(similarities)
        consistency_factor = 1.0 / (1.0 + variance)  # Penalize variance
        
        # Factor 4: Minimum threshold (if weakest doc is bad, confidence is low)
        threshold_factor = 1.0 if min_similarity > 0.3 else min_similarity / 0.3
        
        # Weighted combination
        confidence = (
            evidence_count_factor * 0.25 +        # Evidence quantity (25%)
            avg_similarity * 0.40 +                # Average relevance (40%)
            consistency_factor * 0.20 +            # Consistency (20%)
            threshold_factor * 0.15                # Minimum quality (15%)
        )
        
        # Clamp to 0-1
        return min(1.0, max(0.0, confidence))
    
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
