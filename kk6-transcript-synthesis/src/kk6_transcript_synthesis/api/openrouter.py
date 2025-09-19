"""OpenRouter API client implementation."""

import json
import logging
from typing import Optional

import httpx
from pydantic import ValidationError

from .base import BaseAPIClient, TranscriptAnalysis

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    """OpenRouter API error."""
    pass


class OpenRouterClient(BaseAPIClient):
    """OpenRouter API client for transcript analysis."""
    
    def __init__(self, api_key: str, model: str) -> None:
        """Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            model: Model name to use
        """
        super().__init__(model)
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
                "X-Title": "KK6 Transcript Synthesis",  # Optional but good practice
            },
            timeout=60.0,
        )
    
    async def analyze_transcript(
        self, 
        transcript_content: str, 
        filename: Optional[str] = None
    ) -> TranscriptAnalysis:
        """Analyze transcript using OpenRouter API.
        
        Args:
            transcript_content: The transcript text
            filename: Optional filename for logging
            
        Returns:
            TranscriptAnalysis result
            
        Raises:
            OpenRouterError: If API call fails
        """
        prompt = self._create_analysis_prompt(transcript_content)
        
        try:
            logger.info(f"Analyzing transcript {filename or 'unknown'} with {self.model}")
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,  # Low temperature for consistent analysis
                    "max_tokens": 1000,
                }
            )
            
            if response.status_code != 200:
                error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise OpenRouterError(error_msg)
            
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                raise OpenRouterError("No response choices from OpenRouter API")
            
            content = data["choices"][0]["message"]["content"]
            logger.debug(f"Raw API response: {content}")
            
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
                logger.error(f"Failed to parse API response as JSON: {e}")
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
            error_msg = f"HTTP request failed: {e}"
            logger.error(error_msg)
            raise OpenRouterError(error_msg) from e
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()