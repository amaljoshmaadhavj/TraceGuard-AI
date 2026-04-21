"""
Local LLM client for Ollama integration.

Provides interface to local Ollama service running Phi 2.7B model
for generating investigation insights.
"""

import requests
import json
from typing import Optional, Iterator
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Interface to Ollama local LLM service.
    
    Connects to Ollama instance and generates text using phi:2.7b model.
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434",
                 model: str = "phi:2.7b",
                 timeout: int = 120):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama service endpoint
            model: Model name (must be pulled in Ollama)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        
        logger.info(f"Initialized OllamaClient: {base_url} (model: {model})")
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if service is running and accessible
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama service check failed: {e}")
            return False
    
    def generate(self,
                prompt: str,
                temperature: float = 0.7,
                top_p: float = 0.9) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: Input prompt/context
            temperature: Creativity level (0-1, higher = more creative)
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "top_p": top_p,
            }
            
            logger.debug(f"Sending request to {self.base_url}/api/generate")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return f"Error: Ollama returned {response.status_code}"
            
            # Parse response
            result = response.json()
            generated_text = result.get('response', '')
            
            logger.debug(f"Generated {len(generated_text)} characters")
            return generated_text
        
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama request timed out: {e}")
            raise TimeoutError("Ollama request timed out after 30 seconds") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {e}")
            raise ConnectionError(f"Cannot connect to Ollama service at {self.base_url}") from e
        except Exception as e:
            logger.error(f"Unexpected error in LLM generation: {e}")
            raise RuntimeError(f"Failed to generate summary: {str(e)}") from e
    
    def generate_stream(self,
                       prompt: str,
                       temperature: float = 0.7) -> Iterator[str]:
        """
        Generate response with streaming output.
        
        Args:
            prompt: Input prompt
            temperature: Creativity level
            
        Yields:
            Response tokens as they're generated
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "temperature": temperature,
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code}")
                yield f"Error: {response.status_code}"
                return
            
            # Stream response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        token = data.get('response', '')
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"Error: {str(e)}"
    
    def list_models(self) -> list:
        """
        List available models in Ollama.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code != 200:
                return []
            
            models = response.json().get('models', [])
            return [m.get('name', '') for m in models]
        
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
