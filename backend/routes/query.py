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
    Returns structured timeline if query is timeline-related
    """
    try:
        start_time = time.time()
        query_text = request.get('query', '')
        top_k = request.get('top_k', 10)  # More results for timelines
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Get analyzer
        analyzer_instance = get_analyzer()
        if not analyzer_instance:
            raise HTTPException(status_code=503, detail="System not ready - check Ollama service")
        
        # Check if this is a timeline query
        is_timeline = analyzer_instance.pipeline._detect_timeline_query(query_text)
        
        if is_timeline:
            # Retrieve evidence for timeline
            if not analyzer_instance.pipeline.retriever or not analyzer_instance.pipeline.retriever.is_ready():
                raise HTTPException(status_code=503, detail="Vector database not ready")
            
            evidence = analyzer_instance.pipeline.retriever.retrieve_evidence(query_text, top_k=top_k)
            
            if not evidence:
                return {
                    "query": query_text,
                    "is_timeline": True,
                    "events": [],
                    "summary": "No relevant events found for the specified timeline.",
                    "total_events": 0,
                    "date_range": {"start": "", "end": ""},
                    "confidence": 0.0,
                    "response_time": time.time() - start_time
                }
            
            # Parse into structured events
            events = analyzer_instance.pipeline._parse_evidence_to_events(evidence)
            
            # Get LLM summary with timeout handling
            summary = "Timeline analysis complete."
            try:
                context = analyzer_instance.pipeline._format_evidence_context(evidence)
                summary_prompt = f"""You are a cybersecurity forensic analyst. Based on these timeline events, provide a brief chronological summary of the incident:

{context}

Provide a 2-3 sentence summary of the attack sequence and key findings."""
                summary = analyzer_instance.pipeline.llm_client.generate(summary_prompt, temperature=0.7)
                
                # Check if response is an error message (LLM client returns error strings instead of raising)
                if summary.startswith("Error:"):
                    logger.warning(f"LLM returned error: {summary}")
                    raise Exception(summary)
            except Exception as e:
                logger.warning(f"LLM request failed ({type(e).__name__}), using fallback summary: {e}")
                if events:
                    # Generate intelligent fallback summary from event data
                    categories = set(e['category'] for e in events if e.get('category'))
                    techniques = set()
                    for e in events:
                        if e.get('mitre_techniques'):
                            techniques.update(e['mitre_techniques'])
                    
                    cat_str = ', '.join(sorted(categories))
                    tech_str = ', '.join(sorted(techniques)) if techniques else 'various attack techniques'
                    
                    # Get time range from events
                    timestamps = [e['timestamp'] for e in events if e.get('timestamp')]
                    if timestamps:
                        time_range = f"{min(timestamps)} to {max(timestamps)}"
                    else:
                        time_range = "unknown time range"
                    
                    summary = f"Timeline spans {len(events)} events ({time_range}). " \
                              f"Detected activities include: {cat_str}. MITRE techniques: {tech_str}."
                else:
                    summary = "No events to summarize."
            
            # Extract date range
            timestamps = [e['timestamp'] for e in events if e['timestamp'] != 'N/A']
            date_range = {
                "start": min(timestamps) if timestamps else "",
                "end": max(timestamps) if timestamps else ""
            }
            
            response_time = time.time() - start_time
            
            # Return structured timeline
            return {
                "query": query_text,
                "is_timeline": True,
                "events": events,
                "summary": summary,
                "total_events": len(events),
                "date_range": date_range,
                "confidence": analyzer_instance._calculate_confidence(evidence),
                "response_time": response_time
            }
        else:
            # Regular query
            result = analyzer_instance.analyze(query_text)
            
            response_time = time.time() - start_time
            
            # Format response
            return {
                "query": query_text,
                "is_timeline": False,
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
