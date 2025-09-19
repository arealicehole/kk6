#!/usr/bin/env python3
"""
Quick database check script.
"""

import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def check_database():
    """Check the current state of the database."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        # Check extraction sessions
        sessions = await pool.fetch("""
            SELECT id, session_notes, completed_at, status 
            FROM extraction_sessions 
            ORDER BY completed_at DESC LIMIT 5
        """)
        
        print("Recent Extraction Sessions:")
        for session in sessions:
            print(f"  ID: {session['id']}, Status: {session['status']}, Notes: {session['session_notes'][:50]}...")
            
        # Check planning items
        items = await pool.fetch("""
            SELECT COUNT(*) as count FROM planning_items
        """)
        
        print(f"\nPlanning Items Count: {items[0]['count']}")
        
        # Check if we have any planning items
        if items[0]['count'] > 0:
            sample_items = await pool.fetch("""
                SELECT id, title, category_id, created_at 
                FROM planning_items 
                ORDER BY created_at DESC LIMIT 3
            """)
            
            print("Sample Planning Items:")
            for item in sample_items:
                print(f"  ID: {item['id']}, Title: {item['title'][:40]}...")
                
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(check_database())