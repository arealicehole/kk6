#!/usr/bin/env python3
"""Test vector similarity search with proper dimensions."""

import asyncio
from src.kk6_transcript_synthesis.api.embeddings import OllamaEmbeddingClient
from src.kk6_transcript_synthesis.database import DatabaseManager
from src.kk6_transcript_synthesis.utils import get_settings

async def test_with_proper_dimensions():
    settings = get_settings()
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    embedding_client = OllamaEmbeddingClient(
        host=settings.ollama_host,
        model='nomic-embed-text'
    )
    
    try:
        print('🔍 Testing with proper 768-dimensional embeddings...')
        
        # Generate proper embedding
        query_embedding = await embedding_client.generate_embedding('Kanna Kickback party plans')
        print(f'✅ Generated embedding with {len(query_embedding)} dimensions')
        
        # Verify it's exactly 768 dimensions
        if len(query_embedding) != 768:
            print(f'❌ Wrong dimension! Expected 768, got {len(query_embedding)}')
            return
        
        # Convert to string format  
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
        print(f'🔧 Embedding string: {embedding_str[:50]}... (length: {len(embedding_str)})')
        
        # Test with exact same query that was failing
        test_query = '''
            SELECT filename, mentions_kickback, 
                   embedding <=> $1 AS distance,
                   1 - (embedding <=> $1) AS similarity  
            FROM transcripts 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1
            LIMIT 5
        '''
        
        print('\n🚀 Running similarity search...')
        results = await db_manager.fetch_all(test_query, embedding_str)
        print(f'✅ SUCCESS! Found {len(results)} results')
        
        for i, row in enumerate(results, 1):
            kb_indicator = '🎉' if row['mentions_kickback'] else '📞'
            print(f'   {i}. {kb_indicator} {row["filename"][:50]}...')
            print(f'      Distance: {row["distance"]:.4f}, Similarity: {row["similarity"]:.4f}')
        
        # Test kickback filter
        print('\n🎉 Testing kickback filter...')
        kickback_query = '''
            SELECT filename, mentions_kickback, 
                   1 - (embedding <=> $1) AS similarity  
            FROM transcripts 
            WHERE embedding IS NOT NULL AND mentions_kickback = true
            ORDER BY embedding <=> $1
            LIMIT 5
        '''
        
        kickback_results = await db_manager.fetch_all(kickback_query, embedding_str)
        print(f'✅ Kickback results: {len(kickback_results)}')
        
        for i, row in enumerate(kickback_results, 1):
            print(f'   {i}. 🎉 {row["filename"][:50]}...')
            print(f'      Similarity: {row["similarity"]:.4f}')
    
    finally:
        await embedding_client.close()
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(test_with_proper_dimensions())