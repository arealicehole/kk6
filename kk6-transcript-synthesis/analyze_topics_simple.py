#!/usr/bin/env python3
"""Analyze kickback transcripts for topics using direct LLM text response."""

import asyncio
import httpx
from src.kk6_transcript_synthesis.database import DatabaseManager
from src.kk6_transcript_synthesis.utils import get_settings

async def analyze_with_openrouter(content: str, filename: str) -> str:
    """Direct OpenRouter API call for topic analysis."""
    settings = get_settings()
    
    prompt = f"""Analyze this phone transcript for ALL topics discussed. This is from Gilbert's phone conversations that mention the Kanna Kickback event.

Please provide:
1. **Main Topics Discussed** - List all major subjects/themes covered
2. **Kanna Kickback References** - What specifically is mentioned about the kickback event
3. **Event Planning Details** - Any dates, locations, people, supplies, activities mentioned
4. **Key Information** - Important details for event planning

File: {filename}

Transcript:
{content}

Provide a comprehensive analysis focusing on extracting ALL planning-relevant information."""

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

async def analyze_kickback_transcripts():
    """Analyze each kickback transcript for topics discussed."""
    db = DatabaseManager()
    await db.initialize()
    
    # Get all kickback transcripts
    query = '''
        SELECT id, filename, content, created_at
        FROM transcripts 
        WHERE mentions_kickback = true
        ORDER BY created_at ASC
    '''
    
    results = await db.fetch_all(query)
    print(f"📋 Analyzing {len(results)} kickback transcripts for topics...\n")
    
    analyses = []
    
    for i, row in enumerate(results, 1):
        print(f"{'='*80}")
        print(f"TRANSCRIPT {i}: {row['filename']}")
        print(f"Date: {row['created_at']}")
        print(f"Length: {len(row['content'])} characters")
        print(f"{'='*80}")
        
        try:
            print("🤖 Analyzing with OpenRouter...")
            analysis = await analyze_with_openrouter(row['content'], row['filename'])
            
            print("\n📝 ANALYSIS RESULTS:")
            print("-" * 60)
            print(analysis)
            print("\n" + "="*80 + "\n")
            
            analyses.append({
                'filename': row['filename'],
                'analysis': analysis,
                'date': row['created_at']
            })
            
        except Exception as e:
            print(f"❌ Error analyzing transcript {i}: {e}")
            print("\n" + "="*80 + "\n")
    
    await db.close()
    
    # Save all analyses to a file
    with open('kickback_transcript_analyses.md', 'w') as f:
        f.write("# Kanna Kickback 6 - Transcript Topic Analysis\n\n")
        f.write(f"Analysis of {len(analyses)} transcripts that mention Kanna Kickback\n\n")
        
        for i, analysis in enumerate(analyses, 1):
            f.write(f"## Transcript {i}: {analysis['filename']}\n\n")
            f.write(f"**Date:** {analysis['date']}\n\n")
            f.write(f"{analysis['analysis']}\n\n")
            f.write("---\n\n")
    
    print(f"✅ Analysis complete! Results saved to kickback_transcript_analyses.md")

if __name__ == "__main__":
    asyncio.run(analyze_kickback_transcripts())