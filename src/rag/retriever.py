"""
Evidence retriever for FAISS-based similarity search.

Loads FAISS index and embeddings, retrieves relevant evidence
documents based on query similarity.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
import logging
import os

from ..embeddings.embedding_service import EmbeddingService
from ..storage.faiss_store import FAISSStore

logger = logging.getLogger(__name__)


class Retriever:
    """
    Retrieves relevant evidence documents using FAISS similarity search.
    
    Loads pre-built FAISS index and embeddings model for fast retrieval
    of relevant forensic evidence.
    """
    
    def __init__(self, vectordb_dir: str = "./vectordb"):
        """
        Initialize retriever.
        
        Args:
            vectordb_dir: Directory containing FAISS index and documents
        """
        self.vectordb_dir = vectordb_dir
        self.embedding_service: Optional[EmbeddingService] = None
        self.faiss_store: Optional[FAISSStore] = None
        
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index and embedding model."""
        try:
            # Load FAISS store
            logger.info(f"Loading FAISS index from {self.vectordb_dir}...")
            self.faiss_store = FAISSStore.load(self.vectordb_dir)
            
            # Initialize embedding service
            logger.info("Loading embedding model...")
            self.embedding_service = EmbeddingService(device="cpu")
            
            stats = self.faiss_store.get_stats()
            logger.info(f"Index loaded: {stats['total_documents']} documents, "
                       f"dimension={stats['embedding_dim']}")
        
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            raise
    
    def retrieve_evidence(self, 
                         query: str, 
                         top_k: int = 5) -> List[Dict[str, any]]:
        """
        Retrieve relevant evidence documents for a query.
        
        Args:
            query: Investigator query string
            top_k: Number of documents to retrieve
            
        Returns:
            List of dicts with: document, similarity, metadata
        """
        if not self.embedding_service or not self.faiss_store:
            logger.error("Index not loaded")
            return []
        
        try:
            logger.debug(f"Retrieving top-{top_k} documents for query")
            
            # Embed query
            query_embedding = self.embedding_service.embed_query(query)
            
            # Search FAISS
            results = self.faiss_store.search(query_embedding, top_k=top_k)
            
            # Format results
            formatted_results = []
            for doc, similarity, metadata in results:
                formatted_results.append({
                    'document': doc,
                    'similarity': float(similarity),
                    'metadata': metadata,
                })
            
            logger.debug(f"Retrieved {len(formatted_results)} documents")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []
    
    def is_ready(self) -> bool:
        """
        Check if retriever is ready to use.
        
        Returns:
            True if index is loaded and ready
        """
        return self.faiss_store is not None and self.embedding_service is not None
    
    def get_index_stats(self) -> Dict:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index stats
        """
        if self.faiss_store:
            return self.faiss_store.get_stats()
        return {}
