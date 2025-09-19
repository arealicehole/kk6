#!/usr/bin/env python3
"""
Fix the lifecycle tracking backfill for existing planning items.
"""

import asyncio
import asyncpg
import json
from datetime import datetime

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def fix_lifecycle_backfill():
    """Fix the lifecycle tracking backfill."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        print("🔄 Fixing lifecycle tracking backfill...")
        
        # Get items that need backfill
        items = await pool.fetch("""
            SELECT id, status, created_at, source_id, 
                   first_mentioned_date, last_updated_conversation_id, status_history
            FROM planning_items
            ORDER BY id
        """)
        
        updated_count = 0
        
        for item in items:
            # Check if status_history needs initialization
            status_history = item['status_history'] or []
            
            if not status_history:  # Empty or null status_history
                # Create initial status history entry
                initial_entry = {
                    'status': item['status'],
                    'timestamp': item['created_at'].isoformat(),
                    'conversation_id': item['source_id'],
                    'previous_status': 'new',
                    'notes': 'Initial creation'
                }
                
                status_history = [initial_entry]
                
                # Update the item
                await pool.execute("""
                    UPDATE planning_items SET
                        first_mentioned_date = COALESCE(first_mentioned_date, $2),
                        last_updated_conversation_id = COALESCE(last_updated_conversation_id, $3),
                        status_history = $4
                    WHERE id = $1
                """, 
                item['id'], 
                item['created_at'],
                item['source_id'],
                json.dumps(status_history)
                )
                
                updated_count += 1
                print(f"  ✅ Updated item {item['id']}: {status_history[0]['status']}")
                
        print(f"\n✅ Updated {updated_count} planning items with lifecycle data")
        
        # Test the trigger by updating an item's status
        print("\n🧪 Testing lifecycle tracking trigger...")
        
        test_item = await pool.fetchrow("""
            SELECT id, status, status_history FROM planning_items LIMIT 1
        """)
        
        if test_item:
            print(f"Testing with item {test_item['id']}, current status: {test_item['status']}")
            
            # Update status to trigger the lifecycle tracking
            new_status = 'in_progress' if test_item['status'] != 'in_progress' else 'completed'
            
            await pool.execute("""
                UPDATE planning_items 
                SET status = $2
                WHERE id = $1
            """, test_item['id'], new_status)
            
            # Check the updated lifecycle data
            updated_item = await pool.fetchrow("""
                SELECT id, status, status_history, last_updated_conversation_id
                FROM planning_items WHERE id = $1
            """, test_item['id'])
            
            print(f"  Status changed to: {updated_item['status']}")
            print(f"  Status history entries: {len(updated_item['status_history'])}")
            print(f"  Latest history entry: {updated_item['status_history'][-1]}")
            
        # Show final sample
        print("\n📋 Final sample of lifecycle tracking data:")
        final_samples = await pool.fetch("""
            SELECT id, title, status, first_mentioned_date, 
                   last_updated_conversation_id,
                   jsonb_array_length(status_history) as history_count,
                   status_history->-1 as latest_history
            FROM planning_items 
            ORDER BY id LIMIT 3
        """)
        
        for item in final_samples:
            print(f"  Item {item['id']}: {item['title'][:30]}")
            print(f"    Status: {item['status']}")
            print(f"    First mentioned: {item['first_mentioned_date']}")
            print(f"    History entries: {item['history_count']}")
            print(f"    Latest entry: {item['latest_history']}")
            print()
            
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(fix_lifecycle_backfill())