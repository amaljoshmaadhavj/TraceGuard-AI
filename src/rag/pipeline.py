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
                 model: str = "llama3.2:1b",
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
        Build an advanced prompt for LLM investigation.
        
        Encourages:
        - Structured analysis with specific findings
        - MITRE ATT&CK technique identification
        - Clear timeline and event sequencing
        - Severity assessment
        - Actionable recommendations
        
        Args:
            query: Investigator question
            context: Retrieved evidence context
            
        Returns:
            Formatted prompt for LLM
        """
        is_timeline_query = self._detect_timeline_query(query)
        
        if is_timeline_query:
            prompt = f"""You are an expert cybersecurity forensic investigator analyzing Windows security events.

**CRITICAL INSTRUCTIONS - DO NOT VIOLATE:**
- ONLY use information explicitly present in the provided forensic evidence below.
- Do NOT speculate, assume, invent, or extrapolate beyond what is shown.
- Do NOT claim events indicate "attacks" unless explicitly described as attacks.
- Do NOT estimate time durations (e.g., "3-4 minutes") unless timestamps prove it.
- Do NOT describe "exploits" or "vulnerabilities" unless explicitly mentioned.
- Do NOT fabricate usernames, processes, or technical details not in evidence.
- If evidence is incomplete or unclear, explicitly state this limitation.
- Focus ONLY on what the events ACTUALLY show, based on their descriptions.

INVESTIGATOR QUERY:
{query}

RELEVANT FORENSIC EVIDENCE (ordered by relevance):
{context}

Based ONLY on the forensic evidence provided, construct a detailed TIMELINE ANALYSIS that:

1. **Event Sequence** - List events in chronological order with:
   - Event ID and exact timestamp
   - Source system and user (as shown in evidence)
   - What action occurred (based on event type description)
   - Any relevant parameters or context visible in the evidence

2. **Attack Phases** - Identify phases ONLY if clear evidence supports them:
   - Do not assume phases not demonstrated in the evidence
   - Map observed events to MITRE phases with evidence references

3. **MITRE ATT&CK Techniques** - For each event with available mapping:
   - Technique ID (T####) and official name from evidence
   - Explicit evidence of how technique was observed
   - Avoid speculation about unmapped events

4. **Affected Assets** - Document ONLY what is visible:
   - Systems mentioned in timestamps/metadata
   - User accounts explicitly referenced
   - Resources accessed (only if shown in evidence)

5. **Severity Assessment** - Base on event severity indicators:
   - Use provided severity levels
   - Explain assessment based on event types

6. **Data Quality Note** - State if evidence is incomplete (e.g., missing executable info, unknown user)

Keep response detailed but strictly factual (300-500 words)."""
        
        else:
            prompt = f"""You are an expert cybersecurity investigator analyzing forensic evidence.

**CRITICAL INSTRUCTIONS - DO NOT VIOLATE:**
- ONLY use information explicitly provided in the forensic evidence.
- Do NOT speculate, invent, assume, or extrapolate beyond evidence.
- Do NOT claim without proof that events indicate "attacks" or "exploitation."
- Do NOT describe activities as "unauthorized" unless explicitly stated in evidence.
- Do NOT fabricate timestamps, usernames, process names, or technical parameters not in evidence.
- If data is missing or unclear, explicitly state this as a data quality limitation.
- Be precise: report ONLY what the evidence shows, not what it might suggest.

INVESTIGATOR QUERY:
{query}

RELEVANT FORENSIC EVIDENCE:
{context}

Based ONLY on the forensic evidence provided above, provide a comprehensive investigation analysis that includes:

1. **Findings Summary** - What specific security events are present?
   - List each event with: Event ID, timestamp, and official description
   - State what each event indicates based on its type/classification
   - Do NOT invent interpretations beyond the event definition

2. **Affected Systems & Users** - Document only what is shown:
   - Systems explicitly mentioned in event metadata
   - User names as recorded (note where users are "Unknown")
   - Actual severity levels from the events

3. **Attack Timeline** - Chronological sequence based on timestamps:
   - When activities occurred (using provided timestamps)
   - Order of events as recorded
   - Note any gaps or unclear sequences

4. **MITRE ATT&CK Mapping** - Map events using available references:
   - Technique IDs (T####) from event classification
   - Only for events with defined mappings
   - Reference how technique was observed

5. **Threat Assessment**:
   - Severity: Based on provided event severity levels
   - Confidence: State explicitly if evidence is incomplete
   - Do not estimate likelihood beyond what evidence shows

6. **Recommended Actions**:
   - Immediate steps based on event types
   - Investigation priorities based on evidence quality
   - Preservation requirements for incomplete data

**Important**: If evidence is incomplete (e.g., unknown users, missing process info), explicitly state this as a limitation in your analysis.

Provide analysis suitable for incident response briefing (250-400 words)."""
        
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
            evidence: List of retrieved evidence dicts
            
        Returns:
            List of structured event dicts for timeline
        """
        events = []
        
        for item in evidence:
            doc = item.get('document', '')
            metadata = item.get('metadata', {})
            similarity = item.get('similarity', 0.0)
            
            try:
                # Try to extract from metadata first (structured data)
                event = {
                    'id': metadata.get('id') or f"event_{len(events)}",
                    'event_id': metadata.get('event_id') or self._extract_event_id(doc),
                    'timestamp': metadata.get('timestamp') or self._extract_timestamp(doc),
                    'category': metadata.get('category') or 'Unknown',
                    'severity': metadata.get('metadata', {}).get('severity', 'MEDIUM'),
                    'user': metadata.get('metadata', {}).get('user') or 'Unknown',
                    'computer': metadata.get('metadata', {}).get('computer') or 'Unknown',
                    'description': doc[:300] + '...' if len(doc) > 300 else doc,  # Truncate for display
                    'relevance': f"{similarity:.0%}",
                    'source': metadata.get('filename') or 'Unknown',
                }
                
                events.append(event)
            except Exception as e:
                logger.debug(f"Failed to parse event from evidence: {e}")
                continue
        
        # Sort by timestamp if available
        try:
            events.sort(key=lambda e: e.get('timestamp', ''))
        except Exception:
            pass  # If sorting fails, keep original order
        
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
