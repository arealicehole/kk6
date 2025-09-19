#!/usr/bin/env python3
"""
Add embeddings to planning items for similarity comparison.
"""

import asyncio
import asyncpg
import httpx
from pathlib import Path

# Load configuration
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
EMBEDDING_MODEL = 'nomic-embed-text'
DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def generate_embedding(client, text):
    """Generate embedding for text using Ollama."""
    try:
        response = await client.post(
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
        print(f"Failed to generate embedding: {e}")
        return None

async def add_embeddings_to_planning_items():
    """Add embeddings to planning items that don't have them."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Get planning items without embeddings
        items = await pool.fetch("""
            SELECT id, title, content 
            FROM planning_items 
            WHERE embedding IS NULL
            ORDER BY id
        """)
        
        if not items:
            print("All planning items already have embeddings")
            return
            
        print(f"Adding embeddings to {len(items)} planning items...")
        
        for item in items:
            # Create embedding text from title and content
            embed_text = f"{item['title']}: {item['content']}"
            
            # Generate embedding
            embedding = await generate_embedding(client, embed_text)
            
            if embedding:
                # Convert to PostgreSQL vector format
                embedding_str = f"[{','.join(map(str, embedding))}]"
                
                # Update item with embedding
                await pool.execute("""
                    UPDATE planning_items 
                    SET embedding = $1 
                    WHERE id = $2
                """, embedding_str, item['id'])
                
                print(f"✅ Added embedding to item {item['id']}: {item['title'][:50]}")
            else:
                print(f"❌ Failed to generate embedding for item {item['id']}")
                
    finally:
        await client.aclose()
        await pool.close()

if __name__ == "__main__":
    asyncio.run(add_embeddings_to_planning_items())