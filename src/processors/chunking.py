"""
Document chunking for handling large texts.

Splits documents into appropriately-sized chunks for embedding
while preserving context and metadata.
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Chunks large documents into smaller pieces suitable for embedding.
    
    Preserves document structure and ensures chunks are within
    token limits for embedding models.
    """
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target chunk size in characters (approx 100 chars ≈ 20 tokens)
            overlap: Character overlap between chunks for context
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for text.
        
        Uses rough approximation: 1 token ≈ 4 characters
        
        Args:
            text: Text to estimate
            
        Returns:
            Approximate token count
        """
        return len(text) // 4
    
    def chunk_documents(self, documents: List[str]) -> List[str]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of document strings
            
        Returns:
            List of chunked document strings
        """
        chunks = []
        
        for doc in documents:
            doc_chunks = self.chunk_single(doc)
            chunks.extend(doc_chunks)
        
        logger.info(f"Chunked {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def chunk_single(self, document: str, metadata: Dict = None) -> List[str]:
        """
        Chunk a single document.
        
        Maintains document structure and metadata in chunk text.
        
        Args:
            document: Document string to chunk
            metadata: Optional metadata dict to include in each chunk
            
        Returns:
            List of chunk strings
        """
        if not document:
            return []
        
        # If document is short enough, return as-is
        if len(document) <= self.chunk_size:
            return [document]
        
        chunks = []
        start = 0
        
        while start < len(document):
            # Find a good split point (end of line or sentence)
            end = start + self.chunk_size
            
            if end >= len(document):
                # Last chunk
                chunk = document[start:]
            else:
                # Find natural break point
                break_point = self._find_break_point(document, start, end)
                chunk = document[start:break_point]
                
                # Move start forward, with overlap for context
                start = break_point - self.overlap
            
            if chunk.strip():  # Skip empty chunks
                chunks.append(chunk)
            
            start = break_point
        
        return chunks
    
    @staticmethod
    def _find_break_point(text: str, start: int, preferred_end: int) -> int:
        """
        Find a natural break point (newline or sentence end).
        
        Args:
            text: Full text
            start: Start of current chunk
            preferred_end: Preferred end position
            
        Returns:
            Actual end position (at natural break)
        """
        # Try to break at newline first
        newline_pos = text.rfind('\n', start, preferred_end)
        if newline_pos > start:
            return newline_pos + 1
        
        # Try to break at double space (paragraph)
        para_pos = text.rfind('\n\n', start, preferred_end)
        if para_pos > start:
            return para_pos + 2
        
        # Try to break at sentence end
        for punct in ['. ', '! ', '? ']:
            punct_pos = text.rfind(punct, start, preferred_end)
            if punct_pos > start:
                return punct_pos + 2
        
        # Break at word boundary if possible
        space_pos = text.rfind(' ', start, preferred_end)
        if space_pos > start:
            return space_pos + 1
        
        # Fall back to hard break
        return min(preferred_end, len(text))
    
    def chunk_with_metadata(self, documents: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Chunk documents while preserving metadata.
        
        Args:
            documents: List of dicts with 'text' and optional 'metadata' keys
            
        Returns:
            List of dicts with chunked text and preserved metadata
        """
        chunks = []
        
        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            
            text_chunks = self.chunk_single(text)
            
            for chunk in text_chunks:
                chunks.append({
                    'text': chunk,
                    'metadata': {
                        **metadata,
                        'original_doc_length': len(text),
                    }
                })
        
        return chunks
    
    @staticmethod
    def validate_chunk_size(chunk: str, max_tokens: int = 512) -> bool:
        """
        Validate that a chunk is within token limit.
        
        Args:
            chunk: Chunk text
            max_tokens: Maximum tokens allowed
            
        Returns:
            True if chunk is within limits
        """
        estimated_tokens = DocumentChunker.estimate_tokens(chunk)
        return estimated_tokens <= max_tokens
