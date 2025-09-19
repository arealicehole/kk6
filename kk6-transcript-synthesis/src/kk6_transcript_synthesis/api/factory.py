"""Factory for creating API clients based on configuration."""

from ..utils import APIProvider, get_settings
from .base import BaseAPIClient
from .ollama import OllamaClient
from .openrouter import OpenRouterClient


def get_api_client() -> BaseAPIClient:
    """Create an API client based on current configuration.
    
    Returns:
        Configured API client instance
        
    Raises:
        ValueError: If provider is not supported or configuration is invalid
    """
    settings = get_settings()
    
    if settings.api_provider == APIProvider.OPENROUTER:
        if not settings.openrouter_api_key:
            raise ValueError("OpenRouter API key is required")
        
        return OpenRouterClient(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model
        )
    
    elif settings.api_provider == APIProvider.OLLAMA:
        return OllamaClient(
            host=settings.ollama_host,
            model=settings.ollama_model
        )
    
    else:
        raise ValueError(f"Unsupported API provider: {settings.api_provider}")