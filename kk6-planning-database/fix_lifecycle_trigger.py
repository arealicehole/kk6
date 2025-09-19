#!/usr/bin/env python3
"""
Fix the lifecycle tracking trigger that's creating too many entries.
"""

import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def fix_lifecycle_trigger():
    """Fix the lifecycle tracking trigger."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        print("🔄 Fixing lifecycle tracking trigger...")
        
        # First, drop the problematic trigger
        await pool.execute("DROP TRIGGER IF EXISTS planning_item_lifecycle_trigger ON planning_items;")
        
        # Create a better trigger function that's more careful about updates
        await pool.execute("""
            CREATE OR REPLACE FUNCTION update_planning_item_lifecycle()
            RETURNS TRIGGER AS $$
            BEGIN
                -- Only proceed if this is an INSERT or if specific fields changed
                IF TG_OP = 'INSERT' THEN
                    -- Set first_mentioned_date for new items
                    NEW.first_mentioned_date = COALESCE(NEW.first_mentioned_date, NOW());
                    NEW.last_updated_conversation_id = NEW.source_id;
                    
                    -- Add initial status to history
                    NEW.status_history = COALESCE(NEW.status_history, '[]'::jsonb) || 
                        jsonb_build_array(
                            jsonb_build_object(
                                'status', NEW.status,
                                'timestamp', NOW(),
                                'conversation_id', NEW.source_id,
                                'previous_status', 'new',
                                'notes', 'Item created'
                            )
                        );
                        
                ELSIF TG_OP = 'UPDATE' THEN
                    -- Only update if status actually changed
                    IF NEW.status != OLD.status THEN
                        NEW.last_updated_conversation_id = NEW.source_id;
                        
                        -- Add status change to history
                        NEW.status_history = COALESCE(NEW.status_history, '[]'::jsonb) || 
                            jsonb_build_array(
                                jsonb_build_object(
                                    'status', NEW.status,
                                    'timestamp', NOW(),
                                    'conversation_id', NEW.source_id,
                                    'previous_status', OLD.status,
                                    'notes', 'Status changed'
                                )
                            );
                    END IF;
                    
                    -- Keep first_mentioned_date from original
                    NEW.first_mentioned_date = COALESCE(NEW.first_mentioned_date, OLD.first_mentioned_date);
                END IF;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        print("✅ Updated trigger function")
        
        # Clean up the corrupted data
        print("🧹 Cleaning up corrupted status_history data...")
        
        # Reset status_history for items that got corrupted
        await pool.execute("""
            UPDATE planning_items 
            SET status_history = jsonb_build_array(
                jsonb_build_object(
                    'status', status,
                    'timestamp', created_at,
                    'conversation_id', source_id,
                    'previous_status', 'new',
                    'notes', 'Initial creation (cleaned up)'
                )
            )
            WHERE jsonb_array_length(status_history) > 10  -- Clearly corrupted
        """)
        
        # Initialize status_history for items that don't have it
        await pool.execute("""
            UPDATE planning_items 
            SET 
                first_mentioned_date = COALESCE(first_mentioned_date, created_at),
                last_updated_conversation_id = COALESCE(last_updated_conversation_id, source_id),
                status_history = jsonb_build_array(
                    jsonb_build_object(
                        'status', status,
                        'timestamp', created_at,
                        'conversation_id', source_id,
                        'previous_status', 'new',
                        'notes', 'Initial creation'
                    )
                )
            WHERE status_history IS NULL 
               OR jsonb_array_length(status_history) = 0
        """)
        
        print("✅ Cleaned up status history data")
        
        # Recreate the trigger (only for updates, not inserts to avoid recursion)
        await pool.execute("""
            CREATE TRIGGER planning_item_lifecycle_trigger
                BEFORE INSERT OR UPDATE ON planning_items
                FOR EACH ROW
                EXECUTE FUNCTION update_planning_item_lifecycle();
        """)
        
        print("✅ Recreated trigger")
        
        # Test the fixed trigger
        print("\n🧪 Testing fixed trigger...")
        
        test_item = await pool.fetchrow("""
            SELECT id, status, jsonb_array_length(status_history) as history_count
            FROM planning_items 
            WHERE id = 2  -- Use a different item
        """)
        
        print(f"Test item {test_item['id']}: status={test_item['status']}, history_count={test_item['history_count']}")
        
        # Change status to test trigger
        new_status = 'completed' if test_item['status'] != 'completed' else 'active'
        await pool.execute("""
            UPDATE planning_items SET status = $2 WHERE id = $1
        """, test_item['id'], new_status)
        
        # Check result
        result = await pool.fetchrow("""
            SELECT id, status, jsonb_array_length(status_history) as history_count,
                   status_history->-1 as latest_entry
            FROM planning_items WHERE id = $1
        """, test_item['id'])
        
        print(f"After update: status={result['status']}, history_count={result['history_count']}")
        print(f"Latest entry: {result['latest_entry']}")
        
        # Show clean sample
        print("\n📋 Clean lifecycle tracking sample:")
        samples = await pool.fetch("""
            SELECT id, title, status, first_mentioned_date,
                   jsonb_array_length(status_history) as history_count,
                   status_history
            FROM planning_items 
            ORDER BY id LIMIT 3
        """)
        
        for item in samples:
            print(f"  Item {item['id']}: {item['title'][:30]}")
            print(f"    Status: {item['status']}")
            print(f"    First mentioned: {item['first_mentioned_date']}")
            print(f"    History entries: {item['history_count']}")
            if item['history_count'] > 0:
                print(f"    Latest: {item['status_history'][-1]}")
            print()
            
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(fix_lifecycle_trigger())