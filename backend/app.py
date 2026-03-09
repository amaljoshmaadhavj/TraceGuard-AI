"""
TraceGuard AI Backend - FastAPI Application
Provides REST API interface for cyber investigation system
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import routes
from routes import files, query, stats, processing, settings

# Lazy load heavy modules
_investigation_analyzer = None
_rag_pipeline = None


def get_investigation_analyzer():
    """Lazy load InvestigationAnalyzer on first use"""
    global _investigation_analyzer
    if _investigation_analyzer is None:
        try:
            from src.investigation.analyzer import InvestigationAnalyzer
            _investigation_analyzer = InvestigationAnalyzer()
            logger.info("✅ InvestigationAnalyzer loaded")
        except Exception as e:
            logger.warning(f"⚠️ Could not load InvestigationAnalyzer: {e}")
            _investigation_analyzer = None
    return _investigation_analyzer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 TraceGuard AI Backend starting...")
    yield
    logger.info("🛑 TraceGuard AI Backend shutting down...")


# Create FastAPI app
app = FastAPI(
    title="TraceGuard AI",
    description="Offline Cyber Investigation Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "TraceGuard AI Backend",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "TraceGuard AI",
        "version": "1.0.0"
    }


# Register routes
logger.info("Registering routes...")

# File management routes
app.include_router(files.router, prefix="/api/files", tags=["files"])

# Query routes
app.include_router(query.router, prefix="/api/query", tags=["query"])

# Statistics routes
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])

# Processing routes
app.include_router(processing.router, prefix="/api/processing", tags=["processing"])

# Settings routes
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])

logger.info("✅ All routes registered")


if __name__ == "__main__":
    import uvicorn
    
    # Get host and port from environment
    host = os.getenv("BACKEND_HOST", "localhost")
    port = int(os.getenv("BACKEND_PORT", "8001"))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        timeout_graceful_shutdown=5,
        timeout_keep_alive=30
    )
