#!/usr/bin/env python3
"""Direct query tool for kickback transcripts."""

import asyncio
from src.kk6_transcript_synthesis.database import DatabaseManager

async def query_kickback():
    """Query kickback transcripts directly."""
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        print("🎉 KANNA KICKBACK TRANSCRIPT ANALYSIS\n")
        
        # Get all kickback mentions
        query = """
            SELECT id, filename, content, confidence_score, analysis_notes, created_at
            FROM transcripts 
            WHERE mentions_kickback = true
            ORDER BY confidence_score DESC
        """
        
        results = await db_manager.fetch_all(query)
        print(f"Found {len(results)} transcripts mentioning Kanna Kickback:\n")
        
        for i, row in enumerate(results, 1):
            print(f"📞 {i}. {row['filename']}")
            print(f"   Confidence: {row['confidence_score']}")
            print(f"   Date: {row['created_at'].strftime('%Y-%m-%d')}")
            print(f"   Analysis: {row['analysis_notes']}")
            
            # Show relevant content excerpts
            content = row['content']
            # Look for kickback-related terms
            terms = ['kanna', 'kickback', 'canaker', 'party', 'event']
            excerpts = []
            
            for term in terms:
                if term.lower() in content.lower():
                    start = max(0, content.lower().find(term.lower()) - 50)
                    end = min(len(content), content.lower().find(term.lower()) + 100)
                    excerpt = content[start:end].strip()
                    if excerpt and excerpt not in excerpts:
                        excerpts.append(f"...{excerpt}...")
            
            if excerpts:
                print(f"   Content excerpts:")
                for excerpt in excerpts[:2]:  # Show max 2 excerpts
                    print(f"     \"{excerpt}\"")
            else:
                print(f"   Content preview: \"{content[:150]}...\"")
            
            print()
    
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(query_kickback())