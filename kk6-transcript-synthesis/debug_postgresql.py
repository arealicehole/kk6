#!/usr/bin/env python3
"""Debug PostgreSQL vector operations step by step."""

import asyncio
from src.kk6_transcript_synthesis.api.embeddings import OllamaEmbeddingClient
from src.kk6_transcript_synthesis.database import DatabaseManager
from src.kk6_transcript_synthesis.utils import get_settings

async def debug_step_by_step():
    settings = get_settings()
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    embedding_client = OllamaEmbeddingClient(
        host=settings.ollama_host,
        model='nomic-embed-text'
    )
    
    try:
        print('🔍 Step-by-step PostgreSQL debugging...')
        
        # Step 1: Basic count
        count_query = 'SELECT COUNT(*) as total FROM transcripts WHERE embedding IS NOT NULL'
        count_result = await db_manager.fetch_one(count_query)
        print(f'Step 1 - Total records with embeddings: {count_result["total"]}')
        
        # Step 2: Get one record for testing
        one_query = '''
            SELECT id, filename, mentions_kickback, LEFT(embedding::text, 50) as emb_preview
            FROM transcripts 
            WHERE embedding IS NOT NULL
            LIMIT 1
        '''
        one_result = await db_manager.fetch_one(one_query)
        print(f'Step 2 - Sample record: {one_result["filename"]}, embedding: {one_result["emb_preview"]}...')
        
        # Step 3: Generate test embedding
        test_text = 'test query'
        query_embedding = await embedding_client.generate_embedding(test_text)
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
        print(f'Step 3 - Generated embedding for "{test_text}": {len(query_embedding)} dims')
        
        # Step 4: Test just distance calculation (no ORDER BY)
        dist_query = '''
            SELECT filename, mentions_kickback, embedding <=> $1 AS distance
            FROM transcripts 
            WHERE embedding IS NOT NULL
            LIMIT 3
        '''
        
        print('\nStep 4 - Testing distance calculation...')
        dist_results = await db_manager.fetch_all(dist_query, embedding_str)
        print(f'✅ Distance results: {len(dist_results)}')
        for row in dist_results:
            kb_indicator = '🎉' if row['mentions_kickback'] else '📞'
            print(f'   {kb_indicator} {row["filename"][:40]}... distance: {row["distance"]:.4f}')
        
        if len(dist_results) == 0:
            print('❌ Even distance calculation returns 0 results!')
            # Try with a hardcoded vector from the database
            hardcode_query = '''
                SELECT embedding::text as embedding_text
                FROM transcripts 
                WHERE mentions_kickback = true
                LIMIT 1
            '''
            hardcode_result = await db_manager.fetch_one(hardcode_query)
            if hardcode_result:
                hardcoded_embedding = hardcode_result["embedding_text"]
                print(f'Step 4b - Testing with hardcoded embedding: {hardcoded_embedding[:50]}...')
                
                hardcode_test = '''
                    SELECT filename, mentions_kickback, embedding <=> $1 AS distance
                    FROM transcripts 
                    WHERE embedding IS NOT NULL
                    LIMIT 3
                '''
                hardcode_results = await db_manager.fetch_all(hardcode_test, hardcoded_embedding)
                print(f'✅ Hardcoded results: {len(hardcode_results)}')
        else:
            # Step 5: Test ORDER BY
            print('\nStep 5 - Testing ORDER BY...')
            order_query = '''
                SELECT filename, mentions_kickback, embedding <=> $1 AS distance
                FROM transcripts 
                WHERE embedding IS NOT NULL
                ORDER BY distance
                LIMIT 3
            '''
            
            order_results = await db_manager.fetch_all(order_query, embedding_str)
            print(f'✅ Ordered results: {len(order_results)}')
            for row in order_results:
                kb_indicator = '🎉' if row['mentions_kickback'] else '📞'
                print(f'   {kb_indicator} {row["filename"][:40]}... distance: {row["distance"]:.4f}')
        
    except Exception as e:
        print(f'❌ Error during debugging: {e}')
        import traceback
        traceback.print_exc()
    
    finally:
        await embedding_client.close()
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(debug_step_by_step())