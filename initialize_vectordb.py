#!/usr/bin/env python
"""Initialize vector database from forensic evidence files."""

import os
import sys
import logging
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parsers.evtx_parser import EVTXParser
from embeddings.embedding_service import EmbeddingService
from storage.faiss_store import FAISSStore
from processors.document_builder import DocumentBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _build_evidence_catalog(all_documents: list) -> dict:
    """
    Build comprehensive evidence catalog with statistics.
    
    Args:
        all_documents: List of parsed documents
        
    Returns:
        Dictionary containing evidence by category and statistics
    """
    evidence_by_category = {}
    severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    mitre_techniques = {}
    
    for doc in all_documents:
        category = doc['category']
        if category not in evidence_by_category:
            evidence_by_category[category] = []
        
        # Extract severity if present in metadata
        metadata = doc.get('metadata', {})
        severity = metadata.get('severity', 'MEDIUM')
        if isinstance(severity, dict):
            severity = severity.get('value', 'MEDIUM')
        elif hasattr(severity, 'value'):
            severity = severity.value
        
        severity_str = str(severity).upper().replace('SEVERITY.', '')
        severity_counts[severity_str] = severity_counts.get(severity_str, 0) + 1
        
        # Extract MITRE techniques
        if isinstance(metadata, dict):
            techniques = metadata.get('mitre_techniques', [])
            if techniques:
                for tech in (techniques if isinstance(techniques, list) else [techniques]):
                    mitre_techniques[tech] = mitre_techniques.get(tech, 0) + 1
        
        evidence_by_category[category].append({
            'id': doc['id'],
            'filename': doc['filename'],
            'event_id': doc.get('event_id'),
            'timestamp': doc.get('timestamp'),
            'description': doc['content'][:200],  # Truncate for size
            'severity': severity_str,
            'category': category,
        })
    
    # Build top techniques
    top_techniques = sorted(
        [(f"T{tech.split('T')[1] if 'T' in tech else tech}", count) 
         for tech, count in mitre_techniques.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return {
        'total_events': len(all_documents),
        'total_files': len(set(doc['filename'] for doc in all_documents)),
        'evidence': evidence_by_category,
        'severity_distribution': {
            'critical': severity_counts.get('CRITICAL', 0),
            'high': severity_counts.get('HIGH', 0),
            'medium': severity_counts.get('MEDIUM', 0),
            'low': severity_counts.get('LOW', 0),
        },
        'top_techniques': top_techniques,
        'all_techniques': mitre_techniques,
        'timestamp': datetime.utcnow().isoformat(),
    }


def initialize_vectordb():
    """Initialize FAISS vector database from EVTX files."""
    
    vectordb_dir = "./vectordb"
    data_dir = "./data"
    data_parsed_dir = "./data_parsed"
    embeddings_dir = "./embeddings"
    
    # Create directories
    os.makedirs(vectordb_dir, exist_ok=True)
    os.makedirs(data_parsed_dir, exist_ok=True)
    os.makedirs(embeddings_dir, exist_ok=True)
    
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
                                'content': DocumentBuilder.build_event_document(event),
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
                                'content': DocumentBuilder.build_event_document(event.model_dump()),
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
        
        # Save embeddings cache
        embeddings_path = os.path.join(embeddings_dir, "embeddings.npy")
        logger.info(f"Caching embeddings to {embeddings_path}...")
        embedding_service.save_embeddings(embeddings_array, embeddings_path)
        
        logger.info(f"Adding {len(document_texts)} embeddings to FAISS...")
        # Add all documents and embeddings at once
        faiss_store.add_documents(
            embeddings=embeddings_array,
            documents=document_texts,
            metadata=metadata_list
        )
        
        # Save FAISS index to disk
        logger.info(f"Saving FAISS index to {vectordb_dir}...")
        faiss_store.save(vectordb_dir)
        
        # Build and save evidence catalog to data_parsed
        logger.info(f"Building evidence catalog for data_parsed/...")
        evidence_catalog = _build_evidence_catalog(all_documents)
        
        catalog_path = os.path.join(data_parsed_dir, "evidence_catalog.json")
        with open(catalog_path, 'w') as f:
            json.dump(evidence_catalog, f, indent=2, default=str)
        logger.info(f"Saved evidence catalog to {catalog_path}")
        
        logger.info(f"\n✅ Vector database pipeline initialized successfully!")
        logger.info(f"  📁 Data Pipeline Flow:")
        logger.info(f"    1. ✓ EVTX files parsed: {len(all_documents)} events")
        logger.info(f"    2. ✓ Parsed data saved: {catalog_path}")
        logger.info(f"    3. ✓ Embeddings cached: {embeddings_path}")
        logger.info(f"    4. ✓ FAISS index created: {vectordb_dir}/faiss_index.bin")
        logger.info(f"  📊 Statistics:")
        logger.info(f"    • Documents indexed: {len(document_texts)}")
        logger.info(f"    • Embedding dimension: {embeddings_array.shape[1]}")
        logger.info(f"    • Total events: {evidence_catalog['total_events']}")
        logger.info(f"    • Event categories: {len(evidence_catalog['evidence'])}")
        logger.info(f"    • Severity: {evidence_catalog['severity_distribution']}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error building index: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = initialize_vectordb()
    sys.exit(0 if success else 1)
