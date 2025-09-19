#!/usr/bin/env python3
"""
Test the temporal superseding logic with the created test data.
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def test_temporal_superseding():
    """Test temporal superseding logic with current data."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        print("🔍 Testing temporal superseding logic...")
        
        # Find newer items that might supersede older ones
        # Look for items with similar content but newer timestamps
        superseding_candidates = await pool.fetch("""
            WITH newer_items AS (
                SELECT 
                    pi_new.id as newer_id,
                    pi_new.title as newer_title,
                    pi_new.content as newer_content,
                    pi_new.created_at as newer_created,
                    pi_new.category_id as newer_category,
                    pi_new.embedding as newer_embedding
                FROM planning_items pi_new
                WHERE pi_new.id IN (11, 12, 13, 14)  -- The newer test items we created
                    AND pi_new.superseded_by IS NULL
                    AND pi_new.embedding IS NOT NULL
            ),
            older_items AS (
                SELECT 
                    pi_old.id as older_id,
                    pi_old.title as older_title,
                    pi_old.content as older_content,
                    pi_old.created_at as older_created,
                    pi_old.category_id as older_category,
                    pi_old.embedding as older_embedding
                FROM planning_items pi_old
                WHERE pi_old.id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)  -- The older test items
                    AND pi_old.superseded_by IS NULL
                    AND pi_old.embedding IS NOT NULL
            )
            SELECT 
                newer_items.newer_id,
                newer_items.newer_title,
                newer_items.newer_created,
                older_items.older_id,
                older_items.older_title,
                older_items.older_created,
                1 - (newer_items.newer_embedding <=> older_items.older_embedding) as similarity,
                EXTRACT(EPOCH FROM (newer_items.newer_created - older_items.older_created)) / 3600 as hours_apart
            FROM newer_items, older_items
            WHERE newer_items.newer_category = older_items.older_category  -- Same category
                AND 1 - (newer_items.newer_embedding <=> older_items.older_embedding) >= 0.65  -- High similarity
                AND newer_items.newer_created > older_items.older_created  -- Newer must be after older
            ORDER BY similarity DESC, hours_apart ASC
        """)
        
        if not superseding_candidates:
            print("❌ No superseding candidates found")
            
            # Debug: show what items we have
            items = await pool.fetch("""
                SELECT id, title, created_at, category_id
                FROM planning_items 
                ORDER BY created_at DESC
            """)
            
            print(f"\nFound {len(items)} planning items:")
            for item in items:
                print(f"  ID: {item['id']}, Created: {item['created_at']}, Title: {item['title'][:50]}")
                
            return
            
        print(f"✅ Found {len(superseding_candidates)} potential superseding relationships:")
        
        for i, candidate in enumerate(superseding_candidates, 1):
            hours_gap = candidate['hours_apart']
            similarity = candidate['similarity']
            
            print(f"\n{i}. Superseding Candidate (Similarity: {similarity:.3f}, Gap: {hours_gap:.1f}h)")
            print(f"   Newer  [{candidate['newer_id']}]: {candidate['newer_title']}")
            print(f"   Older  [{candidate['older_id']}]: {candidate['older_title']}")
            
            # Calculate confidence
            confidence = similarity
            if hours_gap < 24:  # Boost for same-day updates
                confidence = min(1.0, confidence + 0.1)
                
            print(f"   Confidence: {confidence:.3f}")
            
            # Apply superseding if high confidence
            if confidence >= 0.79:
                print(f"   🔄 Applying superseding relationship...")
                
                async with pool.acquire() as conn:
                    async with conn.transaction():
                        # Mark older item as superseded
                        await conn.execute(
                            "UPDATE planning_items SET superseded_by = $1 WHERE id = $2",
                            candidate['newer_id'],
                            candidate['older_id']
                        )
                        
                        # Update newer item to record what it supersedes
                        current_supersedes = await conn.fetchval(
                            "SELECT supersedes FROM planning_items WHERE id = $1",
                            candidate['newer_id']
                        )
                        
                        new_supersedes = (current_supersedes or []) + [candidate['older_id']]
                        
                        await conn.execute(
                            "UPDATE planning_items SET supersedes = $1 WHERE id = $2",
                            new_supersedes,
                            candidate['newer_id']
                        )
                        
                print(f"   ✅ Applied: Item {candidate['newer_id']} supersedes Item {candidate['older_id']}")
            else:
                print(f"   ⏭️  Skipped: Confidence too low ({confidence:.3f} < 0.8)")
                
        # Show final state
        print("\n📊 Final Planning Items State:")
        final_items = await pool.fetch("""
            SELECT id, title, superseded_by, supersedes
            FROM planning_items 
            ORDER BY id
        """)
        
        for item in final_items:
            status = "ACTIVE"
            if item['superseded_by']:
                status = f"SUPERSEDED by {item['superseded_by']}"
            elif item['supersedes']:
                status = f"SUPERSEDES {item['supersedes']}"
                
            print(f"  Item {item['id']}: {item['title'][:40]}... [{status}]")
        
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(test_temporal_superseding())