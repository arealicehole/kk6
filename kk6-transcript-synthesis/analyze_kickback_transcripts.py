#!/usr/bin/env python3
"""Analyze each kickback transcript for topics and planning information."""

import asyncio
from src.kk6_transcript_synthesis.database import DatabaseManager
from src.kk6_transcript_synthesis.api.factory import get_api_client

async def analyze_kickback_transcripts():
    """Analyze each kickback transcript for topics discussed."""
    db = DatabaseManager()
    await db.initialize()
    
    llm_client = get_api_client()
    
    # Get all kickback transcripts
    query = '''
        SELECT id, filename, content, created_at
        FROM transcripts 
        WHERE mentions_kickback = true
        ORDER BY created_at ASC
    '''
    
    results = await db.fetch_all(query)
    print(f"📋 Analyzing {len(results)} kickback transcripts for topics...\n")
    
    for i, row in enumerate(results, 1):
        print(f"{'='*60}")
        print(f"TRANSCRIPT {i}: {row['filename']}")
        print(f"Date: {row['created_at']}")
        print(f"Length: {len(row['content'])} characters")
        print(f"{'='*60}")
        
        # Create analysis prompt
        analysis_prompt = f"""
Analyze this phone transcript for ALL topics discussed. This is from Gilbert's phone conversations that mention the Kanna Kickback event.

Please provide:
1. **Main Topics Discussed** - List all major subjects/themes covered
2. **Kanna Kickback References** - What specifically is mentioned about the kickback event
3. **Event Planning Details** - Any dates, locations, people, supplies, activities mentioned
4. **Key Quotes** - Important direct quotes related to planning

Transcript:
{row['content']}

Provide a comprehensive analysis focusing on extracting ALL planning-relevant information.
"""

        try:
            print("🤖 Analyzing with LLM...")
            analysis = await llm_client.analyze_transcript(analysis_prompt)
            
            print("\n📝 ANALYSIS RESULTS:")
            print("-" * 40)
            print(analysis.explanation)
            print("\n" + "="*60 + "\n")
            
        except Exception as e:
            print(f"❌ Error analyzing transcript {i}: {e}")
            print("\n" + "="*60 + "\n")
    
    await llm_client.close()
    await db.close()

if __name__ == "__main__":
    asyncio.run(analyze_kickback_transcripts())