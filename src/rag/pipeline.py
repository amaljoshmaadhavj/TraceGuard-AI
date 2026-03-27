"""
RAG pipeline orchestration.

Combines evidence retrieval with LLM generation to answer
investigative queries with relevant forensic context.
"""

from typing import List, Dict, Optional
import logging

from .retriever import Retriever
from .llm_client import OllamaClient

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.
    
    Retrieves relevant evidence and generates investigation insights
    using local LLM with context from forensic data.
    """
    
    def __init__(self, 
                 vectordb_dir: str = "./vectordb",
                 ollama_url: str = "http://localhost:11434",
                 model: str = "phi:2.7b",
                 top_k: int = 5):
        """
        Initialize RAG pipeline.
        
        Args:
            vectordb_dir: FAISS vector database directory
            ollama_url: Ollama service endpoint
            model: LLM model name
            top_k: Number of evidence documents to retrieve
        """
        self.top_k = top_k
        
        # Initialize components
        try:
            logger.info("Initializing retriever...")
            self.retriever = Retriever(vectordb_dir)
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            self.retriever = None
        
        logger.info("Initializing LLM client...")
        self.llm_client = OllamaClient(
            base_url=ollama_url,
            model=model,
            timeout=120
        )
    
    def is_ready(self) -> bool:
        """
        Check if pipeline is ready.
        
        Returns:
            True if both retriever and LLM are available
        """
        retriever_ok = self.retriever and self.retriever.is_ready()
        llm_ok = self.llm_client.is_available()
        
        if not retriever_ok:
            logger.warning("Retriever not ready")
        if not llm_ok:
            logger.warning("LLM service not available")
        
        return retriever_ok and llm_ok
    
    def answer_query(self, query: str) -> str:
        """
        Answer an investigator query using RAG.
        
        Args:
            query: Investigator question
            
        Returns:
            Investigation summary with recommendations
        """
        if not self.retriever or not self.retriever.is_ready():
            return "Error: Vector database not loaded. Run Stage 3 (03_init_vector_db.py) first."
        
        # Retrieve relevant evidence
        logger.info(f"Retrieving evidence for query: {query[:80]}...")
        evidence = self.retriever.retrieve_evidence(query, top_k=self.top_k)
        
        if not evidence:
            return "No relevant evidence found for this query."
        
        # Format evidence for LLM context
        context = self._format_evidence_context(evidence)
        
        # Build prompt for LLM
        prompt = self._build_investigation_prompt(query, context)
        
        # Generate response
        logger.info("Generating investigation response...")
        response = self.llm_client.generate(prompt, temperature=0.7)
        
        return response
    
    def _format_evidence_context(self, evidence: List[Dict]) -> str:
        """
        Format retrieved evidence for LLM context.
        
        Args:
            evidence: List of retrieved evidence dicts
            
        Returns:
            Formatted context string
        """
        context = ""
        
        for i, item in enumerate(evidence, 1):
            doc = item.get('document', 'N/A')
            similarity = item.get('similarity', 0.0)
            
            # Truncate long documents
            if len(doc) > 500:
                doc = doc[:500] + "...[truncated]"
            
            context += f"\n[EVIDENCE {i} - Relevance: {similarity:.2%}]\n"
            context += doc
            context += "\n"
        
        return context
    
    def _build_investigation_prompt(self, query: str, context: str) -> str:
        """
        Build prompt for LLM.
        
        Args:
            query: Investigator question
            context: Retrieved evidence context
            
        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""You are an expert cybersecurity investigator analyzing forensic evidence.

INVESTIGATOR QUERY:
{query}

RELEVANT FORENSIC EVIDENCE:
{context}

Based on the forensic evidence provided above, provide a concise investigation summary that includes:

1. **Suspicious Activity Detected** - What specific security events or patterns indicate compromise?
2. **Affected Systems & Users** - Which systems, processes, or user accounts are involved?
3. **Timeline** - When did these activities occur?
4. **Attack Techniques** - List any MITRE ATT&CK techniques (T####) if evident from the evidence
5. **Severity Assessment** - How critical is this threat?
6. **Recommended Actions** - What immediate actions should the security team take?

Provide your analysis in a structured format suitable for incident response team briefing.
Keep the response concise but comprehensive (200-400 words)."""
        
        return prompt
    
    def debug_evidence(self, query: str) -> List[Dict]:
        """
        Retrieve and return raw evidence for debugging.
        
        Args:
            query: Query string
            
        Returns:
            Raw list of evidence dicts
        """
        if not self.retriever or not self.retriever.is_ready():
            return []
        
        return self.retriever.retrieve_evidence(query, top_k=self.top_k)
