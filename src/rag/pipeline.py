"""
RAG pipeline orchestration.

Combines evidence retrieval with LLM generation to answer
investigative queries with relevant forensic context.
"""

from typing import List, Dict, Optional
import logging

from .retriever import Retriever
from .llm_client import OllamaClient

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.
    
    Retrieves relevant evidence and generates investigation insights
    using local LLM with context from forensic data.
    """
    
    def __init__(self, 
                 vectordb_dir: str = "./vectordb",
                 ollama_url: str = "http://localhost:11434",
                 model: str = "phi:2.7b",
                 top_k: int = 5):
        """
        Initialize RAG pipeline.
        
        Args:
            vectordb_dir: FAISS vector database directory
            ollama_url: Ollama service endpoint
            model: LLM model name
            top_k: Number of evidence documents to retrieve
        """
        self.top_k = top_k
        
        # Initialize components
        try:
            logger.info("Initializing retriever...")
            self.retriever = Retriever(vectordb_dir)
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            self.retriever = None
        
        logger.info("Initializing LLM client...")
        self.llm_client = OllamaClient(
            base_url=ollama_url,
            model=model,
            timeout=120
        )
    
    def is_ready(self) -> bool:
        """
        Check if pipeline is ready.
        
        Returns:
            True if both retriever and LLM are available
        """
        retriever_ok = self.retriever and self.retriever.is_ready()
        llm_ok = self.llm_client.is_available()
        
        if not retriever_ok:
            logger.warning("Retriever not ready")
        if not llm_ok:
            logger.warning("LLM service not available")
        
        return retriever_ok and llm_ok
    
    def answer_query(self, query: str) -> str:
        """
        Answer an investigator query using RAG.
        
        Args:
            query: Investigator question
            
        Returns:
            Investigation summary with recommendations
        """
        if not self.retriever or not self.retriever.is_ready():
            return "Error: Vector database not loaded. Run Stage 3 (03_init_vector_db.py) first."
        
        # Retrieve relevant evidence
        logger.info(f"Retrieving evidence for query: {query[:80]}...")
        evidence = self.retriever.retrieve_evidence(query, top_k=self.top_k)
        
        if not evidence:
            return "No relevant evidence found for this query."
        
        # Format evidence for LLM context
        context = self._format_evidence_context(evidence)
        
        # Build prompt for LLM
        prompt = self._build_investigation_prompt(query, context)
        
        # Generate response
        logger.info("Generating investigation response...")
        response = self.llm_client.generate(prompt, temperature=0.7)
        
        return response
    
    def _format_evidence_context(self, evidence: List[Dict]) -> str:
        """
        Format retrieved evidence for LLM context.
        
        Args:
            evidence: List of retrieved evidence dicts
            
        Returns:
            Formatted context string
        """
        context = ""
        
        for i, item in enumerate(evidence, 1):
            doc = item.get('document', 'N/A')
            similarity = item.get('similarity', 0.0)
            
            # Truncate long documents
            if len(doc) > 500:
                doc = doc[:500] + "...[truncated]"
            
            context += f"\n[EVIDENCE {i} - Relevance: {similarity:.2%}]\n"
            context += doc
            context += "\n"
        
        return context
    
    def _build_investigation_prompt(self, query: str, context: str) -> str:
        """
        Build prompt for LLM.
        
        Args:
            query: Investigator question
            context: Retrieved evidence context
            
        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""You are an expert cybersecurity investigator analyzing forensic evidence.

INVESTIGATOR QUERY:
{query}

RELEVANT FORENSIC EVIDENCE:
{context}

Based on the forensic evidence provided above, provide a concise investigation summary that includes:

1. **Suspicious Activity Detected** - What specific security events or patterns indicate compromise?
2. **Affected Systems & Users** - Which systems, processes, or user accounts are involved?
3. **Timeline** - When did these activities occur?
4. **Attack Techniques** - List any MITRE ATT&CK techniques (T####) if evident from the evidence
5. **Severity Assessment** - How critical is this threat?
6. **Recommended Actions** - What immediate actions should the security team take?

Provide your analysis in a structured format suitable for incident response team briefing.
Keep the response concise but comprehensive (200-400 words)."""
        
        return prompt
    
    def debug_evidence(self, query: str) -> List[Dict]:
        """
        Retrieve and return raw evidence for debugging.
        
        Args:
            query: Query string
            
        Returns:
            Raw list of evidence dicts
        """
        if not self.retriever or not self.retriever.is_ready():
            return []
        
        return self.retriever.retrieve_evidence(query, top_k=self.top_k)
    
    def _detect_timeline_query(self, query: str) -> bool:
        """
        Detect if query is asking for timeline/sequence of events.
        
        Args:
            query: Query string
            
        Returns:
            True if query is timeline-related
        """
        timeline_keywords = [
            'timeline', 'sequence', 'order', 'chronological',
            'when did', 'what was the order', 'events on',
            'what happened', 'occurred on', 'activity on',
            'sequence of events', 'happened first', 'happened then'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in timeline_keywords)
    
    def _extract_timestamp(self, doc: str) -> str:
        """
        Extract timestamp from document text.
        
        Args:
            doc: Document text
            
        Returns:
            ISO format timestamp string
        """
        import re
        from datetime import datetime
        
        # Try to find ISO format timestamp (YYYY-MM-DDTHH:MM:SS or similar)
        iso_pattern = r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'
        match = re.search(iso_pattern, doc)
        if match:
            return match.group(0)
        
        # Return current timestamp if not found
        return datetime.utcnow().isoformat()
    
    def _extract_event_id(self, doc: str) -> int:
        """Extract event ID from document."""
        import re
        pattern = r'(?:event[_\s]?id|EventID)[:\s]*(\d+)'
        match = re.search(pattern, doc, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _extract_field(self, doc: str, field_name: str) -> str:
        """Extract a named field from document."""
        import re
        # Try multiple patterns
        patterns = [
            rf'{field_name}[:\s]*([^\n,]+)',
            rf'(?:^|\n)\s*{field_name}:\s*([^\n]+)',
            rf'<{field_name}>([^<]+)</{field_name}>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, doc, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value:
                    return value
        
        return 'N/A'
    
    def _parse_evidence_to_events(self, evidence: List[Dict]) -> List[Dict]:
        """
        Parse retrieved documents into structured timeline events.
        Uses both document text and metadata for rich event information.
        
        Args:
            evidence: List of retrieved evidence dicts with document and metadata
            
        Returns:
            Sorted list of timeline events
        """
        from datetime import datetime
        
        events = []
        
        for item in evidence:
            doc = item.get('document', '')
            metadata = item.get('metadata', {})
            
            # Try to extract from metadata first, fall back to document parsing
            if metadata:
                # Use structured metadata if available
                raw_xml = metadata.get('raw_xml', '')
                
                # Extract actual EventID from XML (not metadata.event_id which is 0)
                event_id_from_xml = self._extract_from_xml(raw_xml, 'EventID')
                try:
                    actual_event_id = int(event_id_from_xml) if event_id_from_xml else 0
                except (ValueError, TypeError):
                    logger.debug(f"Failed to parse event_id '{event_id_from_xml}', using 0")
                    actual_event_id = 0
                
                # Get description from CommandLine, RuleName, or ObjectName
                description = (
                    self._extract_from_xml(raw_xml, 'CommandLine') or
                    self._extract_from_xml(raw_xml, 'RuleName') or
                    self._extract_from_xml(raw_xml, 'ObjectName') or
                    metadata.get('description', 'Security Event')
                )
                
                event = {
                    'timestamp': self._parse_timestamp(metadata.get('timestamp', '')),
                    'event_id': actual_event_id,
                    'source_system': metadata.get('computer', metadata.get('source', 'N/A')),
                    'user': metadata.get('user', self._extract_from_xml(raw_xml, 'SubjectUserName') or 'N/A'),
                    'process_name': metadata.get('process_name', self._extract_from_xml(raw_xml, 'Image')),
                    'process_id': metadata.get('process_id', self._extract_from_xml(raw_xml, 'ProcessId')),
                    'description': description or 'N/A',
                    'category': metadata.get('category', 'unknown'),
                    'severity': metadata.get('severity', 'info'),
                    'mitre_techniques': self._extract_mitre_from_xml(raw_xml),
                    'parent_process': self._extract_from_xml(raw_xml, 'ParentImage'),
                    'source_ip': self._extract_from_xml(raw_xml, 'SourceIp'),
                    'dest_ip': self._extract_from_xml(raw_xml, 'DestinationIp')
                }
            else:
                # Fallback to document parsing
                event = {
                    'timestamp': self._extract_timestamp(doc),
                    'event_id': self._extract_event_id(doc),
                    'source_system': self._extract_field(doc, 'computer'),
                    'user': self._extract_field(doc, 'user'),
                    'process_name': self._extract_field(doc, 'process'),
                    'process_id': None,
                    'description': doc[:300] if len(doc) > 300 else doc,
                    'category': self._extract_field(doc, 'category'),
                    'severity': self._extract_field(doc, 'severity'),
                    'mitre_techniques': self._extract_mitre_techniques(doc),
                    'parent_process': None,
                    'source_ip': None,
                    'dest_ip': None
                }
            
            events.append(event)
        
        # Sort by timestamp
        try:
            events.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace(' ', 'T')))
        except (ValueError, TypeError, AttributeError):
            logger.warning("Could not sort events by timestamp")
        
        return events
    
    def _extract_mitre_techniques(self, doc: str) -> List[str]:
        """Extract MITRE ATT&CK technique IDs from document."""
        import re
        pattern = r'\b[Tt]\d{4}(?:\.\d{3})?\b'
        matches = re.findall(pattern, doc)
        return list(set(matches))  # Remove duplicates
    
    def _parse_timestamp(self, ts_str: str) -> str:
        """
        Parse and normalize timestamp string to ISO format.
        
        Args:
            ts_str: Timestamp string in various formats
            
        Returns:
            ISO format timestamp string (YYYY-MM-DDTHH:MM:SS)
        """
        from datetime import datetime
        
        if not ts_str or ts_str == 'N/A':
            return datetime.utcnow().isoformat()
        
        # Try common formats
        formats = [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S+00:00',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(ts_str.replace('+00:00', ''), fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        # If all parsing fails, return as-is
        return ts_str
    
    def _extract_from_xml(self, xml_str: str, tag_name: str) -> Optional[str]:
        """
        Extract value from XML data element.
        
        Args:
            xml_str: XML string
            tag_name: Data element Name attribute value
            
        Returns:
            Extracted value or None
        """
        import re
        if not xml_str:
            return None
        
        # Try Data Name pattern first (for EventData fields)
        pattern = rf'<Data Name="{tag_name}"[^>]*>([^<]+)</Data>'
        match = re.search(pattern, xml_str)
        if match:
            value = match.group(1).strip()
            return value if value and value != '-' else None
        
        # Try direct XML tag pattern (for System fields like EventID, Computer, etc.)
        # This needs to handle attributes like Qualifiers="" in <EventID Qualifiers="">4656</EventID>
        pattern = rf'<{tag_name}(?:\s[^>]*)?>([^<]*)</{tag_name}>'
        match = re.search(pattern, xml_str)
        if match:
            value = match.group(1).strip()
            return value if value and value != '-' else None
        
        return None
    
    def _extract_mitre_from_xml(self, xml_str: str) -> List[str]:
        """
        Extract MITRE ATT&CK techniques from XML RuleName field.
        
        Args:
            xml_str: XML string
            
        Returns:
            List of technique IDs
        """
        import re
        if not xml_str:
            return []
        
        # Look for RuleName with technique_id pattern
        rule_pattern = r'<Data Name="RuleName"[^>]*>([^<]+)</Data>'
        match = re.search(rule_pattern, xml_str)
        
        techniques = []
        if match:
            rule_name = match.group(1)
            # Extract technique_id=T#### patterns
            tech_pattern = r'technique_id=(T\d{4}(?:\.\d{3})?)'  
            tech_matches = re.findall(tech_pattern, rule_name)
            techniques.extend(tech_matches)
        
        # Also look for T#### patterns anywhere in XML
        tech_pattern = r'\b([Tt]\d{4}(?:\.\d{3})?)\b'
        all_matches = re.findall(tech_pattern, xml_str)
        techniques.extend(all_matches)
        
        return list(set(techniques))  # Remove duplicates
