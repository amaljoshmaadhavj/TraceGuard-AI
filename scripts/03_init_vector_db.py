#!/usr/bin/env python3
"""
Stage 3: Initialize FAISS vector database.

Loads embeddings and documents, creates FAISS index,
and persists to disk for RAG retrieval.

Usage:
    python 03_init_vector_db.py [--embeddings-dir ./embeddings] [--vectordb-dir ./vectordb]
"""

import argparse
import sys
import os
import json
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings.embedding_service import EmbeddingService
from src.storage.faiss_store import FAISSStore
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Initialize FAISS vector database with embeddings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                             # Default behavior
  %(prog)s --embeddings-dir ./emb      # Custom embeddings directory
  %(prog)s --vectordb-dir ./my_faiss   # Custom vectordb directory
        """
    )
    
    parser.add_argument(
        '--embeddings-dir',
        default='./embeddings',
        help='Directory with embeddings (default: ./embeddings)'
    )
    parser.add_argument(
        '--vectordb-dir',
        default='./vectordb',
        help='Output directory for vectordb (default: ./vectordb)'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    
    logger.info("=" * 60)
    logger.info("TraceGuard AI - Stage 3: Vector Database Initialization")
    logger.info("=" * 60)
    logger.info(f"Embeddings directory: {args.embeddings_dir}")
    logger.info(f"Vector DB directory: {args.vectordb_dir}")
    
    # Create output directory
    os.makedirs(args.vectordb_dir, exist_ok=True)
    
    try:
        # Load embeddings
        embeddings_path = os.path.join(args.embeddings_dir, 'embeddings.npy')
        documents_path = os.path.join(args.embeddings_dir, 'documents.pkl')
        
        if not os.path.exists(embeddings_path):
            logger.error(f"Embeddings not found: {embeddings_path}")
            logger.error("Please run Stage 2 (02_build_embeddings.py) first.")
            return 1
        
        if not os.path.exists(documents_path):
            logger.error(f"Documents not found: {documents_path}")
            logger.error("Please run Stage 2 (02_build_embeddings.py) first.")
            return 1
        
        logger.info("Loading embeddings...")
        embeddings = EmbeddingService.load_embeddings(embeddings_path)
        logger.info(f"Loaded embeddings: {embeddings.shape}")
        
        logger.info("Loading documents...")
        documents = EmbeddingService.load_documents(documents_path)
        logger.info(f"Loaded {len(documents)} documents")
        
        # Verify dimensions match
        if embeddings.shape[0] != len(documents):
            logger.error(f"Mismatch: {embeddings.shape[0]} embeddings vs {len(documents)} documents")
            return 1
        
        # Initialize FAISS store
        logger.info("\nInitializing FAISS index...")
        embedding_dim = embeddings.shape[1]
        store = FAISSStore(embedding_dim=embedding_dim, index_type="flat")
        
        # Add documents and embeddings
        logger.info("Adding documents to index...")
        metadata = [{'doc_id': i} for i in range(len(documents))]
        store.add_documents(embeddings, documents, metadata)
        
        # Get and log stats
        stats = store.get_stats()
        logger.info(f"\nIndex statistics:")
        logger.info(f"  Type: {stats['index_type']}")
        logger.info(f"  Dimension: {stats['embedding_dim']}")
        logger.info(f"  Total documents: {stats['total_documents']}")
        logger.info(f"  Index size: {stats['index_size']}")
        
        # Save index
        logger.info(f"\nSaving index to {args.vectordb_dir}...")
        store.save(args.vectordb_dir)
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"VECTOR DATABASE READY: {stats['total_documents']} documents indexed")
        logger.info(f"{'=' * 60}\n")
        
        logger.info(f"\nTo start investigating, run:")
        logger.info(f"  python ./scripts/04_run_investigation.py")
        logger.info("\n[OK] Stage 3 complete. Ready for Stage 4: Investigation queries")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error initializing vector database: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
