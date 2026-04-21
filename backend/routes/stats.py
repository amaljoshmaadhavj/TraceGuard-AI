"""
Statistics routes
"""

from fastapi import APIRouter, HTTPException
import sys
import os
import json
import logging
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PARSED_DIR = PROJECT_ROOT / "data_parsed"


@router.get("/")
async def get_statistics():
    """
    Get system statistics from evidence catalog
    """
    try:
        # Load evidence catalog - use absolute path
        catalog_path = DATA_PARSED_DIR / "evidence_catalog.json"
        
        if not os.path.exists(catalog_path):
            logger.warning("Evidence catalog not found. Run initialize_vectordb.py first.")
            return {
                "total_events": 0,
                "total_files": 0,
                "total_techniques": 0,
                "events_by_category": {},
                "severity_distribution": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                },
                "techniques_list": []
            }
        
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        # Count events by category from evidence
        events_by_category = {}
        evidence = catalog.get('evidence', {})
        
        for category, events in evidence.items():
            events_by_category[category] = len(events) if isinstance(events, list) else 0
        
        # Get real severity distribution from catalog
        severity_distribution = catalog.get('severity_distribution', {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        })
        
        # Build techniques list from top_techniques
        techniques_list = []
        top_techniques = catalog.get('top_techniques', [])
        for tech_id, count in top_techniques:
            # Try to get descriptive name from mapping
            tech_names = {
                'T1003': 'OS Credential Dumping',
                'T1021': 'Remote Services',
                'T1059': 'Command and Scripting Interpreter',
                'T1078': 'Valid Accounts',
                'T1570': 'Lateral Tool Transfer',
                'T1562': 'Impair Defenses',
                'T1036': 'Masquerading',
                'T1566': 'Phishing',
                'T1189': 'Drive-by Compromise',
                'T1005': 'Data from Local System',
            }
            tech_name = tech_names.get(tech_id, f"Technique {tech_id}")
            techniques_list.append(f"{tech_id} - {tech_name}")
        
        return {
            "total_events": catalog.get('total_events', 0),
            "total_files": catalog.get('total_files', 0),
            "total_techniques": len(techniques_list),
            "events_by_category": events_by_category,
            "severity_distribution": severity_distribution,
            "techniques_list": techniques_list
        }
    
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_timeline():
    """
    Get event timeline
    """
    try:
        # Load events and sort by timestamp - use absolute path
        catalog_path = DATA_PARSED_DIR / "evidence_catalog.json"
        
        if not os.path.exists(catalog_path):
            return {"timeline": []}
        
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        timeline = []
        for category, events in catalog.get('evidence', {}).items():
            if isinstance(events, list):
                for event in events[:5]:  # Limit to 5 per category
                    timeline.append({
                        "timestamp": event.get('timestamp', ''),
                        "category": category,
                        "description": event.get('description', ''),
                        "severity": event.get('severity', 'unknown')
                    })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {"timeline": timeline[:20]}  # Return first 20
    
    except Exception as e:
        logger.error(f"Timeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
