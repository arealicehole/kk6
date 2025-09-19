#!/usr/bin/env python3
"""
Apply the lifecycle tracking migration to the database.
"""

import asyncio
import asyncpg
from pathlib import Path

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def apply_lifecycle_migration():
    """Apply the lifecycle tracking migration."""
    
    # Read the migration SQL
    migration_path = Path("add_lifecycle_tracking_fields.sql")
    if not migration_path.exists():
        print("❌ Migration file not found: add_lifecycle_tracking_fields.sql")
        return
        
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    # Apply the migration
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        print("🔄 Applying lifecycle tracking migration...")
        
        async with pool.acquire() as conn:
            # Execute the migration in a transaction
            async with conn.transaction():
                await conn.execute(migration_sql)
                
        print("✅ Lifecycle tracking migration applied successfully!")
        
        # Verify the new columns exist
        columns = await pool.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'planning_items' 
                AND column_name IN ('first_mentioned_date', 'last_updated_conversation_id', 'status_history')
            ORDER BY column_name
        """)
        
        print("\n📊 New lifecycle tracking columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
        # Show sample data
        sample_items = await pool.fetch("""
            SELECT id, title, first_mentioned_date, last_updated_conversation_id, 
                   jsonb_array_length(status_history) as history_entries
            FROM planning_items 
            ORDER BY id LIMIT 5
        """)
        
        print("\n📋 Sample planning items with lifecycle data:")
        for item in sample_items:
            print(f"  Item {item['id']}: {item['title'][:40]}")
            print(f"    First mentioned: {item['first_mentioned_date']}")
            print(f"    Last updated conversation: {item['last_updated_conversation_id']}")
            print(f"    Status history entries: {item['history_entries']}")
            print()
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(apply_lifecycle_migration())