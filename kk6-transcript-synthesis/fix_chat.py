#!/usr/bin/env python3
"""Quick fix for the chat search functionality."""

import asyncio
from src.kk6_transcript_synthesis.api.embeddings import OllamaEmbeddingClient
from src.kk6_transcript_synthesis.database import DatabaseManager
from src.kk6_transcript_synthesis.utils import get_settings

async def test_search_fix():
    """Test and demonstrate the working search."""
    settings = get_settings()
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    embedding_client = OllamaEmbeddingClient(
        host=settings.ollama_host,
        model="nomic-embed-text"
    )
    
    try:
        print("🔍 Testing search for Kanna Kickback plans...")
        
        # Generate embedding for kickback query
        query_embedding = await embedding_client.generate_embedding("Kanna Kickback plans party event")
        
        # Use the correct format that works with the database
        embedding_str = str(query_embedding).replace(' ', '')  # Remove ALL spaces
        
        # Search all transcripts first
        all_query = """
            SELECT 
                id, filename, mentions_kickback,
                1 - (embedding <=> $1) AS similarity_score
            FROM transcripts 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1
            LIMIT 10
        """
        
        all_results = await db_manager.fetch_all(all_query, embedding_str)
        print(f"✅ Found {len(all_results)} total results")
        
        for i, row in enumerate(all_results[:5], 1):
            kickback_indicator = "🎉" if row['mentions_kickback'] else "📞"
            print(f"   {i}. {kickback_indicator} {row['filename']} (similarity: {row['similarity_score']:.3f})")
        
        # Now search only kickback mentions
        kickback_query = """
            SELECT 
                id, filename, content, mentions_kickback,
                1 - (embedding <=> $1) AS similarity_score
            FROM transcripts 
            WHERE embedding IS NOT NULL AND mentions_kickback = true
            ORDER BY embedding <=> $1
            LIMIT 5
        """
        
        kickback_results = await db_manager.fetch_all(kickback_query, embedding_str)
        print(f"\n🎉 Found {len(kickback_results)} Kanna Kickback mentions:")
        
        for i, row in enumerate(kickback_results, 1):
            print(f"\n   {i}. {row['filename']} (similarity: {row['similarity_score']:.3f})")
            content_preview = row['content'][:200] + "..." if len(row['content']) > 200 else row['content']
            print(f"      Preview: {content_preview}")
        
        if len(kickback_results) == 0:
            print("   No kickback transcripts found with current embedding")
            
            # Let's check what kickback transcripts exist
            check_query = "SELECT id, filename, LEFT(content, 100) as preview FROM transcripts WHERE mentions_kickback = true LIMIT 3"
            check_results = await db_manager.fetch_all(check_query)
            print(f"\n📋 Available kickback transcripts ({len(check_results)}):")
            for row in check_results:
                print(f"   - {row['filename']}: {row['preview']}...")
    
    finally:
        await embedding_client.close()
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(test_search_fix())