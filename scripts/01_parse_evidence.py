#!/usr/bin/env python3
"""
Stage 1: Parse all forensic evidence files.

Scans data directories and parses all EVTX and PCAP files,
extracting structured events for downstream processing.

Usage:
    python 01_parse_evidence.py [--data-dir ./data] [--output-dir ./data_parsed]
"""

import argparse
import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processors.evidence_aggregator import EvidenceAggregator
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Parse forensic evidence files (EVTX, PCAP)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Default behavior
  %(prog)s --data-dir ./evidence              # Custom data directory
  %(prog)s --output-dir ./parsed_output       # Custom output directory
        """
    )
    
    parser.add_argument(
        '--data-dir',
        default='./data',
        help='Root directory containing evidence files (default: ./data)'
    )
    parser.add_argument(
        '--output-dir',
        default='./data_parsed',
        help='Output directory for parsed results (default: ./data_parsed)'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    
    logger.info("=" * 60)
    logger.info("TraceGuard AI - Stage 1: Evidence Parsing")
    logger.info("=" * 60)
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Verify data directory exists
    if not os.path.exists(args.data_dir):
        logger.error(f"Data directory not found: {args.data_dir}")
        return 1
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Initialize aggregator
        logger.info("Initializing evidence aggregator...")
        aggregator = EvidenceAggregator()
        
        # Scan and parse all evidence
        logger.info(f"Scanning evidence in {args.data_dir}...")
        evidence = aggregator.scan_and_parse(args.data_dir)
        
        # Calculate statistics
        total_events = sum(len(events) for events in evidence.values())
        logger.info(f"\n{'=' * 60}")
        logger.info(f"PARSING COMPLETE: {total_events} total events/packets extracted")
        logger.info(f"{'=' * 60}\n")
        
        # Print summary by category
        for category, events in evidence.items():
            if events:
                logger.info(f"  {category:25} : {len(events):6} events")
        
        # Save catalog
        catalog_path = os.path.join(args.output_dir, 'evidence_catalog.json')
        aggregator.save_catalog(evidence, catalog_path)
        
        logger.info(f"Evidence catalog saved to: {catalog_path}")
        logger.info("\n[OK] Stage 1 complete. Ready for Stage 2: Embedding generation")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error during evidence parsing: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
