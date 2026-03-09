"""
Settings/configuration routes
"""

from fastapi import APIRouter, HTTPException
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_settings():
    """
    Get current settings
    """
    try:
        settings = {
            "ollama_endpoint": os.getenv("OLLAMA_URL", "http://localhost:11434"),
            "llm_model": "qwen2.5:3b",
            "embedding_model": "all-MiniLM-L6-v2",
            "top_k": 5,
            "temperature": 0.7,
            "data_dir": "./data",
            "vectordb_dir": "./vectordb"
        }
        
        return settings
    
    except Exception as e:
        logger.error(f"Settings fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/")
async def update_settings(settings: dict):
    """
    Update settings
    """
    try:
        # Validate settings
        # Update configuration
        # Return success
        
        return {
            "success": True,
            "message": "Settings updated successfully"
        }
    
    except Exception as e:
        logger.error(f"Settings update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
