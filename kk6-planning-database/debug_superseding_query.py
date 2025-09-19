#!/usr/bin/env python3
"""
Debug the superseding query step by step.
"""

import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def debug_superseding_query():
    """Debug the superseding query step by step."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        # First check the newer items
        newer_items = await pool.fetch("""
            SELECT id, title, category_id, created_at
            FROM planning_items
            WHERE id IN (11, 12, 13, 14)
                AND superseded_by IS NULL
                AND embedding IS NOT NULL
        """)
        
        print("Newer items:")
        for item in newer_items:
            print(f"  ID: {item['id']}, Category: {item['category_id']}, Title: {item['title']}")
            
        # Check older items
        older_items = await pool.fetch("""
            SELECT id, title, category_id, created_at
            FROM planning_items
            WHERE id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                AND superseded_by IS NULL
                AND embedding IS NOT NULL
        """)
        
        print("\nOlder items:")
        for item in older_items:
            print(f"  ID: {item['id']}, Category: {item['category_id']}, Title: {item['title']}")
            
        # Now check similarity between specific pairs
        print("\n🔍 Checking similarity between specific pairs:")
        
        test_pairs = [
            (13, 3),  # Age policies
            (12, 4),  # Food pricing  
            (11, 7),  # Capacity/attendance
            (14, 8)   # Patio setup
        ]
        
        for newer_id, older_id in test_pairs:
            result = await pool.fetchrow("""
                SELECT 
                    newer.id as newer_id,
                    newer.title as newer_title,
                    newer.category_id as newer_category,
                    older.id as older_id,
                    older.title as older_title,
                    older.category_id as older_category,
                    1 - (newer.embedding <=> older.embedding) as similarity
                FROM planning_items newer, planning_items older
                WHERE newer.id = $1 AND older.id = $2
            """, newer_id, older_id)
            
            if result:
                categories_match = result['newer_category'] == result['older_category']
                similarity = result['similarity']
                meets_threshold = similarity >= 0.65
                
                print(f"  Items {newer_id} -> {older_id}:")
                print(f"    Categories: {result['newer_category']} vs {result['older_category']} (match: {categories_match})")
                print(f"    Similarity: {similarity:.4f} (>= 0.65: {meets_threshold})")
                print(f"    Would qualify: {categories_match and meets_threshold}")
                print()
                
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(debug_superseding_query())