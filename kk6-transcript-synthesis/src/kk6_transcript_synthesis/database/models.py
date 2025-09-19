"""Database models for transcript records."""

from datetime import datetime
from typing import Any, Optional

import numpy as np
from pydantic import BaseModel, Field, field_validator


class TranscriptRecord(BaseModel):
    """Database model for transcript records."""
    
    id: Optional[int] = Field(default=None, description="Auto-generated primary key")
    filename: str = Field(description="Original transcript filename")
    content: str = Field(description="Full transcript text content")
    mentions_kickback: bool = Field(description="Whether transcript mentions Kanna Kickback")
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="AI confidence score (0.0 to 1.0)"
    )
    analysis_notes: str = Field(description="AI analysis explanation")
    embedding: Optional[list[float]] = Field(
        default=None,
        description="Vector embedding of the transcript content"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (file size, processing time, etc.)"
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Record creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Record last update timestamp"
    )
    
    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Ensure filename is not empty."""
        if not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()
    
    @field_validator("embedding", mode="before")
    @classmethod
    def validate_embedding(cls, v: Any) -> Optional[list[float]]:
        """Validate and convert embedding to list of floats."""
        if v is None:
            return None
        
        if isinstance(v, np.ndarray):
            return v.tolist()
        
        if isinstance(v, list):
            try:
                return [float(x) for x in v]
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid embedding values: {e}")
        
        raise ValueError("Embedding must be a list or numpy array")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        from_attributes = True  # Enable ORM mode