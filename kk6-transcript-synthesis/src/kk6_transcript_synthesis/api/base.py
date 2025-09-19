"""Base API client for transcript analysis."""

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel, Field


class TranscriptAnalysis(BaseModel):
    """Result of transcript analysis."""
    
    mentions_kickback: bool = Field(
        description="Whether the transcript mentions Kanna Kickback"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score from 0.0 to 1.0"
    )
    analysis_notes: str = Field(
        description="Brief explanation of the analysis"
    )
    relevant_quotes: list[str] = Field(
        default_factory=list,
        description="Relevant quotes from the transcript if kickback is mentioned"
    )


class BaseAPIClient(ABC):
    """Abstract base class for API clients."""
    
    def __init__(self, model: str) -> None:
        """Initialize the API client.
        
        Args:
            model: Model name to use for analysis
        """
        self.model = model
    
    @abstractmethod
    async def analyze_transcript(
        self, 
        transcript_content: str, 
        filename: Optional[str] = None
    ) -> TranscriptAnalysis:
        """Analyze a transcript for Kanna Kickback mentions.
        
        Args:
            transcript_content: The text content of the transcript
            filename: Optional filename for context
            
        Returns:
            TranscriptAnalysis with results
            
        Raises:
            APIError: If the API call fails
        """
        pass
    
    def _create_analysis_prompt(self, transcript_content: str) -> str:
        """Create the prompt for transcript analysis.
        
        Args:
            transcript_content: The transcript text to analyze
            
        Returns:
            Formatted prompt string
        """
        return f"""
Analyze this transcript to determine if it mentions "Kanna Kickback" or variations of this phrase.

Be aware of potential spelling variations and similar sounding phrases like:
- Kanna Kickback
- Canna Kickback  
- Kana Kickback
- Cannabis Kickback
- Kanna Kick Back
- Any mentions of "kickback" in context of cannabis/kanna events

Instructions:
1. Read through the entire transcript carefully
2. Look for any mentions of the above terms or similar variations
3. Consider the context - is this referring to an event, gathering, or party?
4. Provide a confidence score from 0.0 to 1.0
5. If mentions are found, extract relevant quotes

Respond with a JSON object in this exact format:
{{
    "mentions_kickback": true/false,
    "confidence_score": 0.0-1.0,
    "analysis_notes": "Brief explanation of your analysis",
    "relevant_quotes": ["quote1", "quote2"] or []
}}

Transcript to analyze:
{transcript_content}
"""