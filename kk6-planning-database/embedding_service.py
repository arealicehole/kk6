#!/usr/bin/env python3
"""
KK6 Transcript Embedding Service
Handles vectorization using Ollama and Nomic embeddings for semantic search.
"""

import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

import asyncpg
import httpx
import numpy as np
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration from .env file
def load_env_config():
    """Load configuration from .env file."""
    env_path = Path("../.env")
    config = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    return config

env_config = load_env_config()
OLLAMA_HOST = env_config.get('OLLAMA_HOST', 'http://localhost:11434')
EMBEDDING_MODEL = 'nomic-embed-text'  # Nomic's embedding model via Ollama
DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

class TranscriptChunk(BaseModel):
    """Model for a transcript chunk with metadata."""
    content: str
    chunk_index: int
    word_count: int
    start_position: int
    end_position: int
    metadata: Dict[str, Any] = {}

class EmbeddingService:
    """Service for generating and managing embeddings via Ollama."""
    
    def __init__(self):
        self.db_pool = None
        self.ollama_client = None
        
    async def initialize(self):
        """Initialize database connection and HTTP client."""
        self.db_pool = await asyncpg.create_pool(DATABASE_URL)
        self.ollama_client = httpx.AsyncClient(timeout=30.0)
        
        # Check if Ollama is running and model is available
        await self._check_ollama_status()
        
    async def _check_ollama_status(self):
        """Check if Ollama is running and the embedding model is available."""
        try:
            # Check Ollama status
            response = await self.ollama_client.get(f"{OLLAMA_HOST}/api/tags")
            response.raise_for_status()
            
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if EMBEDDING_MODEL not in model_names:
                logger.warning(f"Model {EMBEDDING_MODEL} not found. Available models: {model_names}")
                logger.info(f"Pulling {EMBEDDING_MODEL} model...")
                await self._pull_model(EMBEDDING_MODEL)
            else:
                logger.info(f"✅ Ollama connected with {EMBEDDING_MODEL} model")
                
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise
            
    async def _pull_model(self, model_name: str):
        """Pull a model from Ollama if not available."""
        try:
            response = await self.ollama_client.post(
                f"{OLLAMA_HOST}/api/pull",
                json={"name": model_name}
            )
            response.raise_for_status()
            logger.info(f"✅ Successfully pulled {model_name}")
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise
            
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Ollama and Nomic."""
        try:
            response = await self.ollama_client.post(
                f"{OLLAMA_HOST}/api/embeddings",
                json={
                    "model": EMBEDDING_MODEL,
                    "prompt": text
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["embedding"]
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
            
    def intelligent_chunk_transcript(self, transcript_content: str) -> List[TranscriptChunk]:
        """
        Intelligently chunk transcript based on conversation flow and content.
        Looks for natural breaks, speaker changes, topic shifts.
        """
        chunks = []
        
        # Clean up the transcript content first
        content = self._clean_transcript(transcript_content)
        
        # Split by potential conversation boundaries
        # Look for speaker changes, long pauses, topic shifts
        sentences = self._split_into_sentences(content)
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for i, sentence in enumerate(sentences):
            # Check if adding this sentence would make chunk too long
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            # Target chunk size: 200-400 words
            word_count = len(potential_chunk.split())
            
            if word_count >= 200 and (word_count >= 400 or self._is_natural_break(sentence, i, sentences)):
                # Finalize current chunk
                if current_chunk:
                    end_position = current_start + len(current_chunk)
                    chunks.append(TranscriptChunk(
                        content=current_chunk.strip(),
                        chunk_index=chunk_index,
                        word_count=len(current_chunk.split()),
                        start_position=current_start,
                        end_position=end_position,
                        metadata=self._extract_chunk_metadata(current_chunk)
                    ))
                    chunk_index += 1
                    
                # Start new chunk
                current_chunk = sentence
                current_start = end_position if chunks else 0
            else:
                current_chunk = potential_chunk
                
        # Add final chunk if exists
        if current_chunk:
            end_position = current_start + len(current_chunk)
            chunks.append(TranscriptChunk(
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                word_count=len(current_chunk.split()),
                start_position=current_start,
                end_position=end_position,
                metadata=self._extract_chunk_metadata(current_chunk)
            ))
            
        logger.info(f"Created {len(chunks)} intelligent chunks")
        return chunks
        
    def _clean_transcript(self, content: str) -> str:
        """Clean transcript content for better processing."""
        # Remove excessive repetition and noise
        content = re.sub(r'(\w+\s+)\1{3,}', r'\1\1', content)  # Remove excessive repetition
        content = re.sub(r'[_.]{50,}', '', content)  # Remove long separator lines
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        return content.strip()
        
    def _split_into_sentences(self, content: str) -> List[str]:
        """Split content into sentences, respecting conversation flow."""
        # Simple sentence splitting - could be enhanced with NLP
        sentences = re.split(r'[.!?]+\s+', content)
        return [s.strip() for s in sentences if s.strip()]
        
    def _is_natural_break(self, sentence: str, index: int, all_sentences: List[str]) -> bool:
        """Determine if this is a natural break point for chunking."""
        # Look for conversation indicators
        break_indicators = [
            "and then", "so anyway", "but anyway", "speaking of", 
            "by the way", "oh yeah", "actually", "wait",
            "let me think", "you know what", "here's the thing"
        ]
        
        sentence_lower = sentence.lower()
        return any(indicator in sentence_lower for indicator in break_indicators)
        
    def _extract_chunk_metadata(self, chunk_content: str) -> Dict[str, Any]:
        """Extract metadata from chunk content."""
        metadata = {}
        
        # Look for dates, numbers, key topics
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', chunk_content)
        if dates:
            metadata['dates_mentioned'] = dates
            
        # Look for numbers that might be attendance, costs, etc.
        numbers = re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b', chunk_content)
        if numbers:
            metadata['numbers_mentioned'] = numbers
            
        # Look for venue/location references
        venue_keywords = ['venue', 'location', 'restaurant', 'patio', 'space']
        if any(keyword in chunk_content.lower() for keyword in venue_keywords):
            metadata['contains_venue_info'] = True
            
        # Look for cannabis references
        cannabis_keywords = ['cannabis', 'weed', 'sushi', 'stoner', 'smoke']
        if any(keyword in chunk_content.lower() for keyword in cannabis_keywords):
            metadata['contains_cannabis_info'] = True
            
        return metadata
        
    async def embed_transcript_chunks(self, source_id: int, chunks: List[TranscriptChunk]) -> int:
        """Generate embeddings for chunks and store in database."""
        embedded_count = 0
        
        for chunk in chunks:
            try:
                # Generate embedding
                embedding = await self.generate_embedding(chunk.content)
                
                # Convert embedding list to string format for PostgreSQL vector type
                embedding_str = f"[{','.join(map(str, embedding))}]"
                
                # Store in database
                query = """
                    INSERT INTO transcript_chunks (
                        source_id, chunk_index, content, embedding, word_count,
                        start_position, end_position, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (source_id, chunk_index) 
                    DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        word_count = EXCLUDED.word_count,
                        start_position = EXCLUDED.start_position,
                        end_position = EXCLUDED.end_position,
                        metadata = EXCLUDED.metadata
                """
                
                await self.db_pool.execute(
                    query,
                    source_id, chunk.chunk_index, chunk.content, embedding_str,
                    chunk.word_count, chunk.start_position, chunk.end_position,
                    json.dumps(chunk.metadata)
                )
                
                embedded_count += 1
                logger.info(f"  ✅ Embedded chunk {chunk.chunk_index} ({chunk.word_count} words)")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to embed chunk {chunk.chunk_index}: {e}")
                continue
                
        logger.info(f"Successfully embedded {embedded_count}/{len(chunks)} chunks")
        return embedded_count
        
    async def embed_categories(self):
        """Generate and store embeddings for all categories."""
        query = "SELECT id, name, description FROM categories WHERE embedding IS NULL"
        categories = await self.db_pool.fetch(query)
        
        embedded_count = 0
        for category in categories:
            try:
                # Create embedding text from name and description
                embed_text = f"{category['name']}: {category['description'] or category['name']}"
                embedding = await self.generate_embedding(embed_text)
                
                # Convert embedding list to string format for PostgreSQL vector type
                embedding_str = f"[{','.join(map(str, embedding))}]"
                
                # Store embedding
                update_query = "UPDATE categories SET embedding = $1 WHERE id = $2"
                await self.db_pool.execute(update_query, embedding_str, category['id'])
                
                embedded_count += 1
                logger.info(f"  ✅ Embedded category: {category['name']}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to embed category {category['name']}: {e}")
                continue
                
        logger.info(f"Embedded {embedded_count} categories")
        return embedded_count
        
    async def process_transcript_file(self, transcript_path: str) -> Dict[str, Any]:
        """Complete processing pipeline for a transcript file."""
        logger.info(f"🔄 Processing transcript: {Path(transcript_path).name}")
        
        # Read transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Create or get source record
        # First check if source exists
        existing_source = await self.db_pool.fetchrow(
            "SELECT id FROM sources WHERE reference = $1", 
            Path(transcript_path).name
        )
        
        if existing_source:
            source_id = existing_source['id']
        else:
            source_query = """
                INSERT INTO sources (type, reference, metadata)
                VALUES ($1, $2, $3)
                RETURNING id
            """
            source_row = await self.db_pool.fetchrow(
                source_query,
                'transcript',
                Path(transcript_path).name,
                json.dumps({
                    "file_size": len(content),
                    "processing_method": "intelligent_chunking_with_embeddings"
                })
            )
            source_id = source_row['id']
        
        # Chunk transcript intelligently
        chunks = self.intelligent_chunk_transcript(content)
        
        # Generate embeddings for chunks
        embedded_count = await self.embed_transcript_chunks(source_id, chunks)
        
        return {
            "source_id": source_id,
            "total_chunks": len(chunks),
            "embedded_chunks": embedded_count,
            "avg_chunk_size": sum(c.word_count for c in chunks) / len(chunks) if chunks else 0
        }
        
    async def find_relevant_chunks_for_category(
        self, 
        category_id: int, 
        source_id: int, 
        threshold: float = 0.4
    ) -> List[Dict[str, Any]]:
        """Find ALL relevant chunks for a category above relevance threshold using semantic search."""
        
        # Use the new threshold-based database function
        query = "SELECT * FROM find_category_chunks_by_threshold($1, $2, $3)"
        rows = await self.db_pool.fetch(query, category_id, source_id, threshold)
        
        return [
            {
                "chunk_id": row["chunk_id"],
                "content": row["content"],
                "relevance_score": float(row["relevance_score"])
            }
            for row in rows
        ]
        
    async def close(self):
        """Clean up resources."""
        if self.ollama_client:
            await self.ollama_client.aclose()
        if self.db_pool:
            await self.db_pool.close()

async def test_embedding_service():
    """Test the embedding service with a sample transcript."""
    service = EmbeddingService()
    
    try:
        await service.initialize()
        
        # First, embed categories
        print(f"\n🔤 Embedding categories...")
        await service.embed_categories()
        
        # Test with one of the ingest files
        ingest_folder = Path("./ingest")
        transcript_files = list(ingest_folder.glob("*.txt")) if ingest_folder.exists() else []
        
        if transcript_files:
            test_file = transcript_files[0]
            result = await service.process_transcript_file(str(test_file))
            
            print(f"\n🎯 Embedding Test Results:")
            print(f"📁 File: {test_file.name}")
            print(f"📊 Chunks created: {result['total_chunks']}")
            print(f"🔢 Chunks embedded: {result['embedded_chunks']}")
            print(f"📝 Average chunk size: {result['avg_chunk_size']:.1f} words")
            
            # Test category-based chunk retrieval
            print(f"\n🔍 Testing category-based chunk search...")
            # Get a category ID
            category_row = await service.db_pool.fetchrow("SELECT id, name FROM categories LIMIT 1")
            if category_row:
                chunks = await service.find_relevant_chunks_for_category(
                    category_row['id'], 
                    result['source_id'],
                    limit=3
                )
                print(f"📋 Found {len(chunks)} relevant chunks for '{category_row['name']}'")
                for i, chunk in enumerate(chunks, 1):
                    print(f"  {i}. Relevance: {chunk['relevance_score']:.3f}")
                    print(f"     Content: {chunk['content'][:100]}...")
        else:
            print("❌ No transcript files found in ./ingest/")
            
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(test_embedding_service())