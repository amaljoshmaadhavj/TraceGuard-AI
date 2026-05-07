"""
File processing routes
"""

from fastapi import APIRouter, HTTPException
import sys
import os
import logging
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


@router.get("/status")
async def get_processing_status():
    """
    Get current processing status with detailed information.
    
    Returns status of vector database initialization pipeline including:
    - Current processing stage
    - Progress percentage
    - Files processed
    - Any errors encountered
    """
    try:
        # Check if directories exist and have content
        data_dir = PROJECT_ROOT / "data"
        vectordb_dir = PROJECT_ROOT / "vectordb"
        embeddings_dir = PROJECT_ROOT / "embeddings"
        data_parsed_dir = PROJECT_ROOT / "data_parsed"
        
        # Count files in data directory
        file_count = 0
        category_info = {}
        if data_dir.exists():
            for category_dir in data_dir.iterdir():
                if category_dir.is_dir():
                    files = list(category_dir.glob('*.evtx')) + list(category_dir.glob('*.pcap'))
                    file_count += len(files)
                    category_info[category_dir.name] = len(files)
        
        # Determine pipeline status
        if vectordb_dir.exists() and (vectordb_dir / "faiss_index.bin").exists():
            status = "complete"
            stage = 3
            progress = 100
            message = "✅ Vector database ready. System is operational."
        elif embeddings_dir.exists() and (embeddings_dir / "embeddings.npy").exists():
            status = "processing"
            stage = 3
            progress = 75
            message = "⏳ Building FAISS index from embeddings..."
        elif data_parsed_dir.exists() and list(data_parsed_dir.glob('*.json')):
            status = "processing"
            stage = 2
            progress = 50
            message = "⏳ Generating embeddings from parsed documents..."
        elif file_count > 0:
            status = "ready"
            stage = 1
            progress = 25
            message = f"✓ {file_count} evidence files ready. Run vector DB initialization."
        else:
            status = "pending"
            stage = 0
            progress = 0
            message = "⚠️ No evidence files uploaded. Upload EVTX or PCAP files to begin."
        
        stage_names = {
            0: "Upload Evidence",
            1: "Parse Evidence",
            2: "Build Embeddings",
            3: "Vector Database"
        }
        
        return {
            "status": status,
            "stage": stage,
            "stage_name": stage_names.get(stage, "Unknown"),
            "progress": progress,
            "message": message,
            "file_count": file_count,
            "categories": category_info,
            "vectordb_ready": (vectordb_dir.exists() and (vectordb_dir / "faiss_index.bin").exists()),
        }
    
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "status": "error",
            "stage": 0,
            "message": f"Error checking status: {str(e)}",
            "progress": 0,
        }


@router.get("/logs")
async def get_processing_logs():
    """
    Get processing logs
    """
    try:
        logs = []
        
        # Read log file if exists
        log_path = "./logs/traceguard.log"
        if os.path.exists(log_path):
            with open(log_path, 'r', errors='ignore') as f:
                logs = f.readlines()[-50:]  # Last 50 lines
        
        return {"logs": logs}
    
    except Exception as e:
        logger.error(f"Logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
