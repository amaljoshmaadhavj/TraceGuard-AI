"""
FAISS vector database storage.

Provides a wrapper around FAISS for storing and retrieving document embeddings.
Handles index creation, persistence, and similarity search.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import logging
import json
import os

try:
    import faiss
except ImportError:
    faiss = None

logger = logging.getLogger(__name__)


class FAISSStore:
    """
    FAISS-based vector store for document embeddings.
    
    Manages embedding storage, indexing, and retrieval for RAG-based
    investigative analysis.
    """
    
    def __init__(self, embedding_dim: int = 384, index_type: str = "flat"):
        """
        Initialize FAISS store.
        
        Args:
            embedding_dim: Dimension of embeddings (default 384 for all-MiniLM-L6-v2)
            index_type: Type of index ('flat' for exact search, 'ivf' for approximate)
        """
        if faiss is None:
            raise ImportError(
                "faiss not installed. "
                "Install with: pip install faiss-cpu or faiss-gpu"
            )
        
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.index = None
        self.documents: List[str] = []
        self.metadata: List[Dict] = []
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Create FAISS index."""
        if self.index_type == "flat":
            # IndexFlatL2: exact L2 distance
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            logger.info(f"Initialized FAISS IndexFlatL2 (dim={self.embedding_dim})")
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")
    
    def add_documents(self, 
                     embeddings: np.ndarray, 
                     documents: List[str],
                     metadata: Optional[List[Dict]] = None):
        """
        Add documents and embeddings to the index.
        
        Args:
            embeddings: Numpy array of shape (n_docs, embedding_dim)
            documents: List of document strings
            metadata: Optional list of metadata dicts per document
        """
        if embeddings.shape[0] != len(documents):
            raise ValueError(f"Embeddings ({embeddings.shape[0]}) and documents ({len(documents)}) count mismatch")
        
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} != {self.embedding_dim}")
        
        # Ensure embeddings are float32 (FAISS requirement)
        embeddings = np.asarray(embeddings, dtype=np.float32)
        
        logger.info(f"Adding {len(documents)} documents to FAISS index")
        
        # Add to index
        self.index.add(embeddings)
        
        # Store documents and metadata
        self.documents.extend(documents)
        
        if metadata is None:
            metadata = [{} for _ in documents]
        elif len(metadata) != len(documents):
            raise ValueError(f"Metadata ({len(metadata)}) and documents ({len(documents)}) count mismatch")
        
        self.metadata.extend(metadata)
        
        logger.info(f"Index now contains {len(self.documents)} documents")
    
    def search(self, 
              query_embedding: np.ndarray, 
              top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding as numpy array (shape: embedding_dim,)
            top_k: Number of results to return
            
        Returns:
            List of (document, distance, metadata) tuples, sorted by relevance
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty, returning no results")
            return []
        
        # Reshape query to 2D array for FAISS
        query = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0:  # Invalid index
                continue
            
            distance = float(distances[0][i])
            # Convert L2 distance to similarity score (lower distance = higher similarity)
            similarity = 1.0 / (1.0 + distance)
            
            doc = self.documents[idx]
            meta = self.metadata[idx] if idx < len(self.metadata) else {}
            
            results.append((doc, similarity, meta))
        
        logger.debug(f"Search returned {len(results)} results (top_k={top_k})")
        return results
    
    def save(self, save_dir: str):
        """
        Save index and metadata to disk.
        
        Args:
            save_dir: Directory to save index and metadata
        """
        os.makedirs(save_dir, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(save_dir, 'faiss_index.bin')
        faiss.write_index(self.index, index_path)
        logger.info(f"Saved FAISS index to {index_path}")
        
        # Save documents
        docs_path = os.path.join(save_dir, 'documents.txt')
        with open(docs_path, 'w', encoding='utf-8') as f:
            for doc in self.documents:
                # Save one document per line (with newlines escaped)
                f.write(doc.replace('\n', '\\n') + '\n')
        logger.info(f"Saved {len(self.documents)} documents to {docs_path}")
        
        # Save metadata
        metadata_path = os.path.join(save_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
        logger.info(f"Saved metadata to {metadata_path}")
        
        # Save index info
        info_path = os.path.join(save_dir, 'index_info.json')
        info = {
            'index_type': self.index_type,
            'embedding_dim': self.embedding_dim,
            'total_documents': len(self.documents),
            'ntotal': self.index.ntotal,
        }
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        logger.info(f"Saved index info to {info_path}")
    
    @staticmethod
    def load(load_dir: str) -> 'FAISSStore':
        """
        Load index and metadata from disk.
        
        Args:
            load_dir: Directory containing saved index and metadata
            
        Returns:
            FAISSStore instance
        """
        # Load index info
        info_path = os.path.join(load_dir, 'index_info.json')
        with open(info_path, 'r') as f:
            info = json.load(f)
        
        # Create store instance
        store = FAISSStore(
            embedding_dim=info['embedding_dim'],
            index_type=info['index_type']
        )
        
        # Load FAISS index
        index_path = os.path.join(load_dir, 'faiss_index.bin')
        store.index = faiss.read_index(index_path)
        logger.info(f"Loaded FAISS index from {index_path}")
        
        # Load documents
        docs_path = os.path.join(load_dir, 'documents.txt')
        with open(docs_path, 'r', encoding='utf-8') as f:
            store.documents = [line.rstrip('\n').replace('\\n', '\n') for line in f]
        logger.info(f"Loaded {len(store.documents)} documents from {docs_path}")
        
        # Load metadata
        metadata_path = os.path.join(load_dir, 'metadata.json')
        with open(metadata_path, 'r') as f:
            store.metadata = json.load(f)
        logger.info(f"Loaded metadata from {metadata_path}")
        
        return store
    
    def get_stats(self) -> Dict:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index stats
        """
        return {
            'index_type': self.index_type,
            'embedding_dim': self.embedding_dim,
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal,
            'is_trained': self.index.is_trained if hasattr(self.index, 'is_trained') else True,
        }
    
    def clear(self):
        """Clear the index and all stored data."""
        self._initialize_index()
        self.documents.clear()
        self.metadata.clear()
        logger.info("Cleared FAISS store")
