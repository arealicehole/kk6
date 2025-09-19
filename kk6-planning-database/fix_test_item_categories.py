#!/usr/bin/env python3
"""
Fix the categories of test items to enable proper superseding testing.
"""

import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def fix_test_item_categories():
    """Fix categories of test items to match their actual content."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        # Update categories for items that should match
        updates = [
            (3, 6, "Age policy for event -> legal_compliance"),  # Move to match item 13
            (4, 2, "Food pricing and revenue share -> food_catering"),  # Move to match item 12
        ]
        
        for item_id, new_category, description in updates:
            await pool.execute("""
                UPDATE planning_items 
                SET category_id = $1 
                WHERE id = $2
            """, new_category, item_id)
            
            print(f"✅ Updated item {item_id}: {description}")
            
        print("\n🔄 Re-checking categories after updates:")
        
        # Check categories again
        items = await pool.fetch("""
            SELECT id, title, category_id
            FROM planning_items 
            WHERE id IN (3, 4, 11, 12, 13, 14)
            ORDER BY id
        """)
        
        for item in items:
            print(f"  ID: {item['id']}, Category: {item['category_id']}, Title: {item['title']}")
            
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(fix_test_item_categories())