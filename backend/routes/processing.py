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
    Get current processing status
    """
    try:
        # Check if directories exist - use absolute paths
        vectordb_exists = (PROJECT_ROOT / "vectordb").exists()
        embeddings_exists = (PROJECT_ROOT / "embeddings").exists()
        data_parsed_exists = (PROJECT_ROOT / "data_parsed").exists()
        
        if vectordb_exists and embeddings_exists and data_parsed_exists:
            status = "complete"
            stage = 3
            progress = 100
        elif embeddings_exists and data_parsed_exists:
            status = "processing"
            stage = 3
            progress = 50
        elif data_parsed_exists:
            status = "processing"
            stage = 2
            progress = 75
        else:
            status = "pending"
            stage = 1
            progress = 0
        
        stage_names = {
            1: "Parse Evidence",
            2: "Build Embeddings",
            3: "Vector Database"
        }
        
        return {
            "stage": stage,
            "stage_name": stage_names.get(stage, "Unknown"),
            "progress": progress,
            "status": status,
            "message": "All data indexed and ready for investigation" if status == "complete" else "Processing forensic evidence..."
        }
    
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
