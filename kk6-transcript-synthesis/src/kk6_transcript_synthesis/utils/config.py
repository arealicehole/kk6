"""Configuration management for KK6 Transcript Synthesis."""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIProvider(str, Enum):
    """Supported API providers."""
    
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # API Configuration
    api_provider: APIProvider = Field(
        default=APIProvider.OPENROUTER,
        description="Which API provider to use (openrouter or ollama)",
    )
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = Field(
        default=None,
        description="OpenRouter API key from .env file",
    )
    openrouter_model: str = Field(
        default="meta-llama/llama-3.2-3b-instruct:free",
        description="OpenRouter model to use",
    )
    
    # Ollama Configuration
    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Ollama API host",
    )
    ollama_model: str = Field(
        default="llama3.2",
        description="Ollama model to use",
    )
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:55432/kk6_transcripts",
        description="PostgreSQL database URL",
    )
    
    # Processing Configuration
    transcript_folder: Path = Field(
        default=Path("../gilbert-transcripts"),
        description="Path to transcript folder",
    )
    batch_size: int = Field(
        default=5,
        description="Number of transcripts to process in batch",
    )
    
    
    @field_validator("transcript_folder", mode="before")
    @classmethod
    def validate_transcript_folder(cls, v: str | Path) -> Path:
        """Convert to Path and resolve."""
        if isinstance(v, str):
            v = Path(v)
        return v.resolve()
    
    def validate_provider_config(self) -> None:
        """Validate that required settings are present for selected provider."""
        if self.api_provider == APIProvider.OPENROUTER:
            if not self.openrouter_api_key:
                raise ValueError(
                    "OpenRouter API key is required. Add OPENROUTER_API_KEY to .env file"
                )
        
        # Validate database URL format
        if not self.database_url.startswith("postgresql://"):
            raise ValueError("Database URL must be a valid PostgreSQL connection string")


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.validate_provider_config()
    return _settings