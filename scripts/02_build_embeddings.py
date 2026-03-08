#!/usr/bin/env python3
"""
Stage 2: Build embeddings for parsed evidence.

Loads parsed evidence catalog, converts events to investigation documents,
chunks documents, and generates vector embeddings.

Usage:
    python 02_build_embeddings.py [--parsed-dir ./data_parsed] [--output-dir ./embeddings]
"""

import argparse
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processors.evidence_aggregator import EvidenceAggregator
from src.processors.document_builder import DocumentBuilder
from src.processors.chunking import DocumentChunker
from src.embeddings.embedding_service import EmbeddingService
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Build embeddings for evidence documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Default behavior
  %(prog)s --parsed-dir ./my_parsed     # Custom parsed data directory
  %(prog)s --output-dir ./my_embeddings # Custom output directory
        """
    )
    
    parser.add_argument(
        '--parsed-dir',
        default='./data_parsed',
        help='Directory with parsed evidence (default: ./data_parsed)'
    )
    parser.add_argument(
        '--output-dir',
        default='./embeddings',
        help='Output directory for embeddings (default: ./embeddings)'
    )
    parser.add_argument(
        '--device',
        default='cpu',
        choices=['cpu', 'cuda', 'mps'],
        help='Device for embeddings (default: cpu)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for embedding generation (default: 32)'
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
    logger.info("TraceGuard AI - Stage 2: Embedding Generation")
    logger.info("=" * 60)
    logger.info(f"Parsed data directory: {args.parsed_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Device: {args.device}")
    logger.info(f"Batch size: {args.batch_size}")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Load evidence catalog
        catalog_path = os.path.join(args.parsed_dir, 'evidence_catalog.json')
        if not os.path.exists(catalog_path):
            logger.error(f"Evidence catalog not found: {catalog_path}")
            logger.error("Please run Stage 1 (01_parse_evidence.py) first.")
            return 1
        
        logger.info(f"Loading evidence catalog from {catalog_path}...")
        aggregator = EvidenceAggregator()
        evidence = aggregator.load_catalog(catalog_path)
        
        total_events = sum(len(events) for events in evidence.values())
        logger.info(f"Loaded {total_events} evidence items")
        
        # Build investigation documents
        logger.info("\nBuilding investigation documents...")
        documents = DocumentBuilder.build_investigation_documents(evidence)
        logger.info(f"Built {len(documents)} investigation documents")
        
        # Chunk documents
        logger.info("\nChunking documents...")
        chunker = DocumentChunker(chunk_size=512, overlap=50)
        chunks = chunker.chunk_documents(documents)
        logger.info(f"Chunked into {len(chunks)} document chunks")
        
        # Generate embeddings
        logger.info(f"\nGenerating embeddings (device={args.device})...")
        embedding_service = EmbeddingService(device=args.device)
        embeddings = embedding_service.embed_documents(
            chunks,
            batch_size=args.batch_size
        )
        logger.info(f"Generated embeddings shape: {embeddings.shape}")
        
        # Save embeddings and documents
        logger.info("\nSaving embeddings and documents...")
        
        embeddings_path = os.path.join(args.output_dir, 'embeddings.npy')
        embedding_service.save_embeddings(embeddings, embeddings_path)
        
        documents_path = os.path.join(args.output_dir, 'documents.pkl')
        EmbeddingService.save_documents(chunks, documents_path)
        
        # Save metadata
        metadata = {
            'timestamp': datetime.utcnow().isoformat(),
            'num_documents': len(chunks),
            'embedding_dim': embeddings.shape[1],
            'embedding_model': 'all-MiniLM-L6-v2',
            'chunk_size': 512,
            'chunk_overlap': 50,
            'device': args.device,
        }
        
        metadata_path = os.path.join(args.output_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"EMBEDDINGS COMPLETE: {len(chunks)} chunks embedded")
        logger.info(f"{'=' * 60}\n")
        logger.info(f"  Embeddings saved: {embeddings_path}")
        logger.info(f"  Documents saved:  {documents_path}")
        logger.info(f"  Metadata saved:   {metadata_path}")
        
        logger.info("\n[OK] Stage 2 complete. Ready for Stage 3: Vector database initialization")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error during embedding generation: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
