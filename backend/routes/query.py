"""
Investigation query routes
"""

from fastapi import APIRouter, HTTPException
import sys
import os
import logging
import time
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import TraceGuard modules
try:
    from src.investigation.analyzer import InvestigationAnalyzer
except ImportError as e:
    logger.warning(f"Could not import InvestigationAnalyzer: {e}")

# Global analyzer instance (initialize once)
analyzer = None

def get_analyzer():
    """Get or create analyzer instance"""
    global analyzer
    if analyzer is None:
        try:
            # Use absolute path to vectordb
            import pathlib
            project_root = pathlib.Path(__file__).parent.parent.parent
            vectordb_path = str(project_root / "vectordb")
            logger.info(f"Loading vectordb from: {vectordb_path}")
            
            analyzer = InvestigationAnalyzer(
                vectordb_dir=vectordb_path,
                ollama_url="http://localhost:11434"
            )
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}", exc_info=True)
            return None
    return analyzer


@router.post("/")
async def submit_query(request: dict):
    """
    Submit an investigation query
    """
    try:
        start_time = time.time()
        query_text = request.get('query', '')
        top_k = request.get('top_k', 5)
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Get analyzer
        analyzer_instance = get_analyzer()
        if not analyzer_instance:
            raise HTTPException(status_code=503, detail="System not ready - check Ollama service")
        
        # Run analysis
        result = analyzer_instance.analyze(query_text)
        
        response_time = time.time() - start_time
        
        # Format response
        return {
            "query": query_text,
            "response": result.response,
            "evidence": [],
            "confidence": result.confidence,
            "techniques": result.techniques if result.techniques else [],
            "response_time": response_time,
            "evidence_count": result.evidence_count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_query_suggestions():
    """
    Get example query suggestions
    """
    suggestions = [
        "What credential dumping activity was detected?",
        "Was lateral movement detected?",
        "What suspicious processes executed?",
        "Show the attack timeline",
        "Which MITRE ATT&CK techniques were used?",
        "What events occurred on the system?",
        "Show high severity events"
    ]
    
    return {"suggestions": suggestions}


@router.get("/history")
async def get_query_history():
    """
    Get query history
    """
    return {"history": []}
