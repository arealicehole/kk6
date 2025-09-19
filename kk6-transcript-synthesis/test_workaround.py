#!/usr/bin/env python3
"""Test workaround for PostgreSQL ORDER BY issue."""

import asyncio
from src.kk6_transcript_synthesis.api.embeddings import OllamaEmbeddingClient
from src.kk6_transcript_synthesis.database import DatabaseManager
from src.kk6_transcript_synthesis.utils import get_settings

async def test_workaround():
    settings = get_settings()
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    embedding_client = OllamaEmbeddingClient(
        host=settings.ollama_host,
        model='nomic-embed-text'
    )
    
    try:
        print('🔍 Testing workaround approaches...')
        
        # Generate test embedding
        query_embedding = await embedding_client.generate_embedding('Kanna Kickback party plans')
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
        print(f'✅ Generated embedding: {len(query_embedding)} dims')
        
        # Approach 1: Use a subquery
        print('\n1. Subquery approach...')
        subquery = '''
            SELECT * FROM (
                SELECT filename, mentions_kickback, 
                       embedding <=> $1 AS distance,
                       1 - (embedding <=> $1) AS similarity
                FROM transcripts 
                WHERE embedding IS NOT NULL
            ) t
            ORDER BY t.distance
            LIMIT 5
        '''
        
        try:
            results1 = await db_manager.fetch_all(subquery, embedding_str)
            print(f'   ✅ Subquery results: {len(results1)}')
            for row in results1[:3]:
                kb_indicator = '🎉' if row['mentions_kickback'] else '📞'
                print(f'   {kb_indicator} {row["filename"][:40]}... similarity: {row["similarity"]:.4f}')
        except Exception as e:
            print(f'   ❌ Subquery failed: {e}')
        
        # Approach 2: Get all results and sort in Python
        print('\n2. Python sorting approach...')
        python_query = '''
            SELECT filename, mentions_kickback, 
                   embedding <=> $1 AS distance,
                   1 - (embedding <=> $1) AS similarity
            FROM transcripts 
            WHERE embedding IS NOT NULL
        '''
        
        try:
            all_results = await db_manager.fetch_all(python_query, embedding_str)
            print(f'   ✅ Got all results: {len(all_results)}')
            
            # Sort by distance in Python
            sorted_results = sorted(all_results, key=lambda x: x['distance'])[:5]
            print(f'   ✅ Top 5 after Python sorting:')
            for i, row in enumerate(sorted_results, 1):
                kb_indicator = '🎉' if row['mentions_kickback'] else '📞'
                print(f'   {i}. {kb_indicator} {row["filename"][:40]}... similarity: {row["similarity"]:.4f}')
            
            # Filter for kickback only
            kickback_results = [r for r in sorted_results if r['mentions_kickback']][:5]
            print(f'\n   🎉 Kickback-only results: {len(kickback_results)}')
            for i, row in enumerate(kickback_results, 1):
                print(f'   {i}. 🎉 {row["filename"][:40]}... similarity: {row["similarity"]:.4f}')
        
        except Exception as e:
            print(f'   ❌ Python sorting failed: {e}')
        
        # Approach 3: Force PostgreSQL to use a different plan  
        print('\n3. Force different query plan...')
        force_query = '''
            SELECT filename, mentions_kickback, 
                   similarity_score
            FROM (
                SELECT filename, mentions_kickback,
                       1 - (embedding <=> $1) AS similarity_score,
                       ROW_NUMBER() OVER (ORDER BY embedding <=> $1) as rn
                FROM transcripts 
                WHERE embedding IS NOT NULL
            ) ranked
            WHERE rn <= 5
            ORDER BY similarity_score DESC
        '''
        
        try:
            results3 = await db_manager.fetch_all(force_query, embedding_str)
            print(f'   ✅ Forced plan results: {len(results3)}')
            for row in results3:
                kb_indicator = '🎉' if row['mentions_kickback'] else '📞'
                print(f'   {kb_indicator} {row["filename"][:40]}... similarity: {row["similarity_score"]:.4f}')
        except Exception as e:
            print(f'   ❌ Forced plan failed: {e}')
    
    finally:
        await embedding_client.close()
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(test_workaround())