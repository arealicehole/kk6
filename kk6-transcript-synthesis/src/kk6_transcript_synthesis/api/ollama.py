"""Ollama API client implementation."""

import json
import logging
from typing import Optional

import httpx
from pydantic import ValidationError

from .base import BaseAPIClient, TranscriptAnalysis

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Ollama API error."""
    pass


class OllamaClient(BaseAPIClient):
    """Ollama API client for transcript analysis."""
    
    def __init__(self, host: str, model: str) -> None:
        """Initialize Ollama client.
        
        Args:
            host: Ollama host URL (e.g., http://localhost:11434)
            model: Model name to use
        """
        super().__init__(model)
        self.host = host.rstrip("/")
        
        self.client = httpx.AsyncClient(
            timeout=120.0,  # Ollama can be slower for large models
        )
    
    async def analyze_transcript(
        self, 
        transcript_content: str, 
        filename: Optional[str] = None
    ) -> TranscriptAnalysis:
        """Analyze transcript using Ollama API.
        
        Args:
            transcript_content: The transcript text
            filename: Optional filename for logging
            
        Returns:
            TranscriptAnalysis result
            
        Raises:
            OllamaError: If API call fails
        """
        prompt = self._create_analysis_prompt(transcript_content)
        
        try:
            logger.info(f"Analyzing transcript {filename or 'unknown'} with Ollama {self.model}")
            
            response = await self.client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent analysis
                        "top_p": 0.9,
                        "num_predict": 1000,
                    }
                }
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise OllamaError(error_msg)
            
            data = response.json()
            
            if "response" not in data:
                raise OllamaError("No response field in Ollama API response")
            
            content = data["response"]
            logger.debug(f"Raw Ollama response: {content}")
            
            # Parse the JSON response
            try:
                # Try to extract JSON from the response
                if "```json" in content:
                    # Extract JSON from code block
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                elif "{" in content and "}" in content:
                    # Find JSON object in response
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    json_str = content[json_start:json_end]
                else:
                    raise ValueError("No JSON found in response")
                
                result_data = json.loads(json_str)
                return TranscriptAnalysis(**result_data)
                
            except (json.JSONDecodeError, ValueError, ValidationError) as e:
                logger.error(f"Failed to parse Ollama response as JSON: {e}")
                logger.error(f"Raw response: {content}")
                
                # Fallback: try to determine if kickback is mentioned
                content_lower = content.lower()
                mentions = any(
                    phrase in content_lower 
                    for phrase in ["mentions", "found", "yes", "true", "kickback"]
                )
                
                return TranscriptAnalysis(
                    mentions_kickback=mentions,
                    confidence_score=0.5,
                    analysis_notes=f"Failed to parse structured response. Raw: {content[:200]}...",
                    relevant_quotes=[]
                )
                
        except httpx.RequestError as e:
            error_msg = f"HTTP request to Ollama failed: {e}"
            logger.error(error_msg)
            raise OllamaError(error_msg) from e
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()