"""
Evidence aggregator for collecting and organizing forensic data.

Scans evidence directories and parses EVTX files, organizing results
by security category for easy access during investigation.
"""

import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging
import json

from ..parsers import EVTXParser, EvidenceMetadata

logger = logging.getLogger(__name__)


class EvidenceAggregator:
    """
    Aggregates evidence from all source files.
    
    Scans data directories, parses EVTX and PCAP files, and organizes
    results by category (credential_access, execution, etc.).
    """
    
    # Standard evidence directory structure
    EVIDENCE_CATEGORIES = [
        'credential_access',
        'execution',
        'lateral_movement',
        'network_logs',
        'collection',
        'exfiltration',
        'discovery',
        'persistence',
        'defense_evasion',
    ]
    
    def __init__(self):
        """Initialize aggregator with EVTX parser."""
        try:
            self.evtx_parser = EVTXParser()
        except ImportError:
            logger.warning("EVTXParser not available (python-evtx not installed)")
            self.evtx_parser = None
    
    def scan_and_parse(self, data_dir: str) -> Dict[str, List[Dict]]:
        """
        Scan evidence directory and parse EVTX files.
        
        Args:
            data_dir: Root path to evidence directory
            
        Returns:
            Dictionary organized by category:
            {
                'credential_access': [EventLogEntry dicts],
                'execution': [EventLogEntry dicts],
                ...
            }
        """
        evidence = {}
        
        logger.info(f"Starting evidence scan in {data_dir}")
        
        # Scan each category directory
        for category in self.EVIDENCE_CATEGORIES:
            category_path = os.path.join(data_dir, category)
            
            if not os.path.exists(category_path):
                logger.debug(f"Category directory not found: {category_path}")
                continue
            
            logger.info(f"Scanning category: {category}")
            evidence[category] = []
            
            # Scan all files in category directory
            for file_name in os.listdir(category_path):
                file_path = os.path.join(category_path, file_name)
                
                if not os.path.isfile(file_path):
                    continue
                
                # Parse EVTX files
                if file_name.lower().endswith('.evtx'):
                    if self.evtx_parser:
                        try:
                            logger.debug(f"Parsing EVTX: {file_path}")
                            result = self.evtx_parser.parse_event_log(file_path)
                            evidence[category].extend(result.events)
                        except Exception as e:
                            logger.error(f"Failed to parse {file_path}: {e}")
                    else:
                        logger.warning(f"Skipping EVTX file (parser not available): {file_path}")
        
        # Log summary
        total_events = sum(len(events) for events in evidence.values())
        logger.info(f"Evidence aggregation complete: {total_events} total events extracted")
        
        return evidence
    
    def scan_specific_category(self, data_dir: str, category: str) -> List[Dict]:
        """
        Scan and parse a single evidence category.
        
        Args:
            data_dir: Root path to evidence directory
            category: Category name (e.g., 'credential_access')
            
        Returns:
            List of parsed event dicts from that category
        """
        events = []
        category_path = os.path.join(data_dir, category)
        
        if not os.path.exists(category_path):
            logger.warning(f"Category directory not found: {category_path}")
            return events
        
        logger.info(f"Scanning category: {category}")
        
        for file_name in os.listdir(category_path):
            file_path = os.path.join(category_path, file_name)
            
            if not os.path.isfile(file_path):
                continue
            
            # Parse EVTX files
            if file_name.lower().endswith('.evtx'):
                if self.evtx_parser:
                    try:
                        result = self.evtx_parser.parse_event_log(file_path)
                        events.extend(result.events)
                    except Exception as e:
                        logger.error(f"Failed to parse {file_path}: {e}")
        
        logger.info(f"Category '{category}': {len(events)} events extracted")
        return events
    
    def enrich_with_severity(self, events: List[Dict]) -> List[Dict]:
        """
        Events already include severity from EVTX parser.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Same events (already contains severity)
        """
        # Events already have severity from EVTXParser
        return events
    
    def save_catalog(self, evidence: Dict[str, List[Dict]], output_path: str):
        """
        Save aggregated evidence catalog to JSON file.
        
        Args:
            evidence: Dictionary of evidence by category
            output_path: Path to save catalog JSON
        """
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        catalog = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_events': sum(len(events) for events in evidence.values()),
            'evidence': evidence,
        }
        
        with open(output_path, 'w') as f:
            json.dump(catalog, f, indent=2, default=str)
        
        logger.info(f"Evidence catalog saved to {output_path}")
    
    def load_catalog(self, catalog_path: str) -> Dict[str, List[Dict]]:
        """
        Load previously saved evidence catalog.
        
        Args:
            catalog_path: Path to catalog JSON file
            
        Returns:
            Dictionary of evidence by category
        """
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        return catalog.get('evidence', {})
