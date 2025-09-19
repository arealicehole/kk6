#!/usr/bin/env python3
"""
Debug similarity scores between planning items.
"""

import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def debug_similarity():
    """Debug similarity scores between planning items."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        # Check similarity between specific items that should be related
        similar_pairs = await pool.fetch("""
            SELECT 
                pi1.id as id1,
                pi1.title as title1,
                pi1.created_at as created1,
                pi2.id as id2,
                pi2.title as title2,
                pi2.created_at as created2,
                1 - (pi1.embedding <=> pi2.embedding) as similarity
            FROM planning_items pi1, planning_items pi2
            WHERE pi1.id != pi2.id
                AND pi1.embedding IS NOT NULL
                AND pi2.embedding IS NOT NULL
                AND pi1.category_id = pi2.category_id  -- Same category
            ORDER BY similarity DESC
            LIMIT 20
        """)
        
        print("🔍 Top similarity scores between planning items:")
        print("=" * 80)
        
        for pair in similar_pairs:
            similarity = pair['similarity']
            time_diff = abs((pair['created1'] - pair['created2']).total_seconds() / 3600)
            
            print(f"Similarity: {similarity:.4f} | Time Gap: {time_diff:.1f}h")
            print(f"  Item {pair['id1']}: {pair['title1']}")
            print(f"  Item {pair['id2']}: {pair['title2']}")
            print()
            
        # Show some specific pairs that we expect to be similar
        print("\n🎯 Checking specific expected similar pairs:")
        
        expected_pairs = [
            ("Age policy for event", "Updated age policy - 21+ only"),
            ("Food pricing and revenue share", "Revised food pricing structure"),
            ("Expected attendance and capacity", "Updated venue capacity requirements"),
            ("Patio area and entry setup", "Final patio setup configuration")
        ]
        
        for title1, title2 in expected_pairs:
            result = await pool.fetchrow("""
                SELECT 
                    pi1.id as id1, pi1.title as title1,
                    pi2.id as id2, pi2.title as title2,
                    1 - (pi1.embedding <=> pi2.embedding) as similarity
                FROM planning_items pi1, planning_items pi2
                WHERE pi1.title = $1 AND pi2.title = $2
                    AND pi1.embedding IS NOT NULL
                    AND pi2.embedding IS NOT NULL
            """, title1, title2)
            
            if result:
                print(f"'{title1}' vs '{title2}': {result['similarity']:.4f}")
            else:
                print(f"Could not find pair: '{title1}' vs '{title2}'")
                
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(debug_similarity())