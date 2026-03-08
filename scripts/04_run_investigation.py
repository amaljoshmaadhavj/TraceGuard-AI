#!/usr/bin/env python3
"""
Stage 4: Interactive investigation CLI.

Provides an interactive REPL for investigators to query
the forensic evidence database using natural language.

Usage:
    python 04_run_investigation.py [--vectordb-dir ./vectordb] [--ollama-url http://localhost:11434]
"""

import argparse
import sys
import os
from pathlib import Path
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.investigation.analyzer import InvestigationAnalyzer
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)


class InvestigationCLI:
    """Interactive investigation interface."""
    
    def __init__(self, analyzer: InvestigationAnalyzer):
        """Initialize CLI."""
        self.analyzer = analyzer
        self.history = []
    
    def display_banner(self):
        """Display welcome banner."""
        print("\n" + "=" * 70)
        print("   TraceGuard AI - Offline Cyber Investigation Assistant")
        print("=" * 70)
        print("\nWelcome, Investigator!")
        print("\nThis system analyzes forensic evidence (EVTX, PCAP) and provides")
        print("investigation insights using local AI powered by Qwen2.5-3B.\n")
        print("System Status:")
        
        if self.analyzer.pipeline.is_ready():
            stats = self.analyzer.pipeline.retriever.get_index_stats()
            print(f"  [OK] Vector Database: {stats.get('total_documents')} documents indexed")
            print(f"  [OK] LLM Service:     Ollama (Qwen2.5-3B) ready")
        else:
            print("  [ERROR] System not ready. Check configuration.")
            print("  Run: python ./scripts/03_init_vector_db.py")
        
        print("\nCommands:")
        print("  help       - Show example queries")
        print("  status     - Show system status")
        print("  quit/exit  - Exit investigation")
        print("\n" + "=" * 70 + "\n")
    
    def display_help(self):
        """Display help and example queries."""
        print("\nExample Investigation Queries:")
        print("-" * 70)
        
        examples = self.analyzer.suggest_queries()
        for i, query in enumerate(examples, 1):
            print(f"  {i}. {query}")
        
        print("\nYou can ask similar questions about your forensic evidence.")
        print("The system will retrieve relevant evidence and provide analysis.\n")
    
    def display_status(self):
        """Display system status."""
        ready = self.analyzer.pipeline.is_ready()
        
        print("\nSystem Status:")
        print("-" * 70)
        
        if ready:
            stats = self.analyzer.pipeline.retriever.get_index_stats()
            print(f"  Status:          [OK] Ready for investigation")
            print(f"  Documents:       {stats.get('total_documents')} indexed")
            print(f"  Embedding Dim:   {stats.get('embedding_dim')}")
            print(f"  Evidence Types:  EVTX (Windows Events), PCAP (Network)")
        else:
            print(f"  Status:          [ERROR] System not ready")
            print(f"  Action Required: Run setup scripts (01, 02, 03)")
        
        print(f"  Queries:         {len(self.history)} completed")
        print("\n")
    
    def process_query(self, query: str) -> bool:
        """
        Process investigator query.
        
        Args:
            query: Query string
            
        Returns:
            True if query processed, False if exit command
        """
        # Check for commands
        cmd = query.strip().lower()
        
        if cmd in ['quit', 'exit']:
            return False
        
        if cmd == 'help':
            self.display_help()
            return True
        
        if cmd == 'status':
            self.display_status()
            return True
        
        if cmd == 'history':
            self._display_history()
            return True
        
        if cmd == 'clear':
            self.history.clear()
            print("History cleared.\n")
            return True
        
        if cmd == '':
            return True
        
        # Process investigation query
        if not self.analyzer.pipeline.is_ready():
            print("\n[ERROR] System not ready.")
            print("Please run setup scripts first:\n")
            print("  1. python ./scripts/01_parse_evidence.py")
            print("  2. python ./scripts/02_build_embeddings.py")
            print("  3. python ./scripts/03_init_vector_db.py\n")
            return True
        
        print("\n[Analyzing...]")
        
        try:
            result = self.analyzer.analyze(query)
            
            # Display response
            print("\n" + "=" * 70)
            print("INVESTIGATION FINDINGS")
            print("=" * 70)
            print(result.response)
            
            # Display metadata
            print("\n" + "-" * 70)
            print("Analysis Metadata:")
            print(f"  Evidence Retrieved: {result.evidence_count}")
            print(f"  Confidence Score:   {result.confidence:.1%}")
            if result.techniques:
                print(f"  MITRE Techniques:   {', '.join(result.techniques)}")
            print("=" * 70 + "\n")
            
            # Add to history
            self.history.append({
                'query': query,
                'evidence_count': result.evidence_count,
                'confidence': result.confidence,
            })
        
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            print(f"\n[ERROR] {str(e)}\n")
        
        return True
    
    def _display_history(self):
        """Display query history."""
        if not self.history:
            print("\nNo queries in history.\n")
            return
        
        print("\nQuery History:")
        print("-" * 70)
        for i, item in enumerate(self.history, 1):
            print(f"  {i}. {item['query'][:60]}")
            print(f"     Evidence: {item['evidence_count']}, Confidence: {item['confidence']:.1%}")
        print("\n")
    
    def run_interactive(self):
        """Run interactive REPL loop."""
        self.display_banner()
        
        while True:
            try:
                # Get user input
                query = input("? ").strip()
                
                # Process query
                if not self.process_query(query):
                    break
            
            except KeyboardInterrupt:
                print("\n\nInvestigation interrupted.")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"\n[ERROR] {e}\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Interactive cyber investigation assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                           # Default
  %(prog)s --vectordb-dir ./vectordb --ollama-url http://localhost:11434

Commands in REPL:
  help    - Show example queries
  status  - Display system information
  history - Show query history
  quit    - Exit
        """
    )
    
    parser.add_argument(
        '--vectordb-dir',
        default='./vectordb',
        help='FAISS vector database directory'
    )
    parser.add_argument(
        '--ollama-url',
        default='http://localhost:11434',
        help='Ollama service endpoint'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    
    # Initialize analyzer
    analyzer = InvestigationAnalyzer(
        vectordb_dir=args.vectordb_dir,
        ollama_url=args.ollama_url
    )
    
    # Run CLI
    cli = InvestigationCLI(analyzer)
    cli.run_interactive()
    
    print("\n[OK] Investigation session ended. Thank you for using TraceGuard AI.\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
