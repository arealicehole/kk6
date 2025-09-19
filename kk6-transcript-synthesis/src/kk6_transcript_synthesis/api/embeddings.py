"""Ollama embedding client for generating vector embeddings."""

import logging
from typing import List

import httpx

logger = logging.getLogger(__name__)


class OllamaEmbeddingError(Exception):
    """Ollama embedding API error."""
    pass


class OllamaEmbeddingClient:
    """Ollama client specifically for generating embeddings."""
    
    def __init__(self, host: str, model: str) -> None:
        """Initialize Ollama embedding client.
        
        Args:
            host: Ollama host URL (e.g., http://localhost:11434)
            model: Embedding model name (e.g., embeddinggemma)
        """
        self.host = host.rstrip("/")
        self.model = model
        
        self.client = httpx.AsyncClient(
            timeout=120.0,  # Embeddings can take time
        )
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
            
        Raises:
            OllamaEmbeddingError: If embedding generation fails
        """
        try:
            logger.debug(f"Generating embedding for text ({len(text)} chars) with {self.model}")
            
            response = await self.client.post(
                f"{self.host}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                }
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama embedding API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise OllamaEmbeddingError(error_msg)
            
            data = response.json()
            
            if "embedding" not in data:
                raise OllamaEmbeddingError("No embedding field in Ollama API response")
            
            embedding = data["embedding"]
            
            if not isinstance(embedding, list) or not embedding:
                raise OllamaEmbeddingError("Invalid embedding format received")
            
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except httpx.RequestError as e:
            error_msg = f"HTTP request to Ollama failed: {e}"
            logger.error(error_msg)
            raise OllamaEmbeddingError(error_msg) from e
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings corresponding to input texts
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                embedding = await self.generate_embedding(text)
                embeddings.append(embedding)
                logger.info(f"Generated embedding {i+1}/{len(texts)}")
            except Exception as e:
                logger.error(f"Failed to generate embedding for text {i+1}: {e}")
                # Add empty embedding as placeholder
                embeddings.append([])
        
        return embeddings
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()