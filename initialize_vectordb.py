#!/usr/bin/env python
"""Initialize vector database from forensic evidence files."""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parsers.evtx_parser import EVTXParser
from embeddings.embedding_service import EmbeddingService
from storage.faiss_store import FAISSStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_vectordb():
    """Initialize FAISS vector database from EVTX files."""
    
    vectordb_dir = "./vectordb"
    data_dir = "./data"
    
    # Create vectordb dir if it doesn't exist
    os.makedirs(vectordb_dir, exist_ok=True)
    
    logger.info("🔍 Scanning for evidence files...")
    
    # Collect all EVTX files
    all_documents = []
    file_count = 0
    event_count = 0
    
    for root, dirs, files in os.walk(data_dir):
        for filename in files:
            if filename.lower().endswith('.evtx'):
                filepath = os.path.join(root, filename)
                logger.info(f"📄 Parsing {filename}...")
                
                try:
                    parser = EVTXParser()
                    result = parser.parse_event_log(filepath)
                    events = result.events
                    
                    for event in events:
                        # Handle both dict and EventLogEntry objects
                        if isinstance(event, dict):
                            all_documents.append({
                                'id': f"{file_count}_{event_count}",
                                'filename': filename,
                                'category': os.path.basename(root),
                                'source': filepath,
                                'content': event.get('description', event.get('brief_description', str(event))),
                                'event_id': event.get('event_id', event.get('EventID')),
                                'computer': event.get('computer', event.get('ComputerName', '')),
                                'timestamp': event.get('timestamp', event.get('TimeCreated', '')),
                                'metadata': event
                            })
                        else:
                            # EventLogEntry object
                            all_documents.append({
                                'id': f"{file_count}_{event_count}",
                                'filename': filename,
                                'category': os.path.basename(root),
                                'source': filepath,
                                'content': event.description,
                                'event_id': event.event_id,
                                'computer': event.computer,
                                'timestamp': event.timestamp.isoformat() if event.timestamp else '',
                                'metadata': {
                                    'event_id': event.event_id,
                                    'severity': event.severity.value,
                                    'security_category': event.category.value,
                                    'source': event.source,
                                    'user': event.user,
                                    'computer': event.computer,
                                    'process_name': event.process_name,
                                    'process_id': event.process_id,
                                }
                            })
                        event_count += 1
                    
                    file_count += 1
                    logger.info(f"  ✓ Extracted {len(events)} events from {filename}")
                
                except Exception as e:
                    logger.error(f"  ✗ Error parsing {filename}: {e}")
    
    if not all_documents:
        logger.error("❌ No documents found to index!")
        return False
    
    logger.info(f"\n📚 Indexing {len(all_documents)} documents ({event_count} events)...")
    
    # Initialize embedding service
    logger.info("Loading embedding model...")
    embedding_service = EmbeddingService(device="cpu")
    
    # Create FAISS store (default embedding_dim=384 for all-MiniLM-L6-v2)
    logger.info("Creating FAISS index...")
    faiss_store = FAISSStore()
    
    # Prepare document texts and metadata
    try:
        logger.info("Preparing documents for embedding...")
        document_texts = []
        metadata_list = []
        
        for doc in all_documents:
            document_texts.append(doc['content'])
            metadata_list.append({
                'id': doc['id'],
                'filename': doc['filename'],
                'category': doc['category'],
                'event_id': doc.get('event_id'),
                'timestamp': doc.get('timestamp'),
                'source': doc.get('source'),
                'metadata': doc.get('metadata', {})
            })
        
        # Generate embeddings for all documents at once
        logger.info(f"Generating embeddings for {len(document_texts)} documents...")
        embeddings_array = embedding_service.embed_documents(document_texts, batch_size=32)
        
        logger.info(f"Adding {len(document_texts)} embeddings to FAISS...")
        # Add all documents and embeddings at once
        faiss_store.add_documents(
            embeddings=embeddings_array,
            documents=document_texts,
            metadata=metadata_list
        )
        
        # Save index to disk
        logger.info(f"Saving index to {vectordb_dir}...")
        faiss_store.save(vectordb_dir)
        
        logger.info(f"\n✅ Vector database initialized!")
        logger.info(f"  • Documents indexed: {len(document_texts)}")
        logger.info(f"  • Embedding dimension: 384")
        logger.info(f"  • Location: {vectordb_dir}")
        logger.info(f"  • Files saved:")
        logger.info(f"    - {os.path.join(vectordb_dir, 'faiss_index.bin')}")
        logger.info(f"    - {os.path.join(vectordb_dir, 'documents.txt')}")
        logger.info(f"    - {os.path.join(vectordb_dir, 'metadata.json')}")
        logger.info(f"    - {os.path.join(vectordb_dir, 'index_info.json')}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error building index: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = initialize_vectordb()
    sys.exit(0 if success else 1)
