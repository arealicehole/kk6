#!/usr/bin/env python3
"""
Apply the conversation temporal fields migration to the sources table.
"""

import asyncio
import asyncpg
from pathlib import Path

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def apply_conversation_temporal_migration():
    """Apply the conversation temporal fields migration."""
    
    # Read the migration SQL
    migration_path = Path("add_conversation_temporal_fields.sql")
    if not migration_path.exists():
        print("❌ Migration file not found: add_conversation_temporal_fields.sql")
        return
        
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        print("🔄 Applying conversation temporal fields migration...")
        
        async with pool.acquire() as conn:
            # Execute the migration in a transaction
            async with conn.transaction():
                await conn.execute(migration_sql)
                
        print("✅ Conversation temporal fields migration applied successfully!")
        
        # Verify the new columns exist
        columns = await pool.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'sources' 
                AND column_name IN (
                    'conversation_date', 'conversation_sequence', 'participants', 
                    'communication_method', 'conversation_duration_minutes'
                )
            ORDER BY column_name
        """)
        
        print("\n📊 New conversation temporal columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
        # Check current sources
        sources = await pool.fetch("""
            SELECT id, reference, conversation_date, conversation_sequence, 
                   participants, communication_method
            FROM sources 
            ORDER BY id
        """)
        
        print(f"\n📋 Current sources ({len(sources)} total):")
        for source in sources:
            print(f"  Source {source['id']}: {source['reference']}")
            print(f"    Date: {source['conversation_date']}")
            print(f"    Sequence: {source['conversation_sequence']}")
            print(f"    Participants: {source['participants']}")
            print(f"    Method: {source['communication_method']}")
            print()
            
        # Test the chronological view
        chrono_view = await pool.fetch("""
            SELECT id, reference, conversation_sequence, planning_items_count
            FROM conversations_chronological
            LIMIT 5
        """)
        
        print("📅 Chronological conversations view:")
        for conv in chrono_view:
            print(f"  {conv['conversation_sequence'] or 'No seq'}: {conv['reference']} ({conv['planning_items_count']} items)")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(apply_conversation_temporal_migration())