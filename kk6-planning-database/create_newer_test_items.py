#!/usr/bin/env python3
"""
Create newer test planning items that might supersede older ones.
"""

import asyncio
import asyncpg
from datetime import datetime, timedelta

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def create_newer_test_items():
    """Create newer test planning items with similar content to test superseding."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        # Get the latest extraction session
        latest_session = await pool.fetchrow("""
            SELECT id, source_id, completed_at 
            FROM extraction_sessions 
            ORDER BY completed_at DESC 
            LIMIT 1
        """)
        
        if not latest_session:
            print("No extraction sessions found")
            return
            
        # Create some newer items that might supersede older ones
        newer_items = [
            {
                "title": "Updated venue capacity requirements",
                "content": "After further discussion, we need to accommodate 250 people instead of the original 200. The venue space needs to be larger.",
                "category_id": 1,  # venue_management
                "confidence_level": 8
            },
            {
                "title": "Revised food pricing structure",
                "content": "New food pricing model with 30% revenue share instead of previous discussions. Includes premium sushi options.",
                "category_id": 2,  # food_catering  
                "confidence_level": 9
            },
            {
                "title": "Updated age policy - 21+ only",
                "content": "After legal consultation, event will be strictly 21+ with mandatory ID checking at entry.",
                "category_id": 6,  # legal_compliance
                "confidence_level": 9
            },
            {
                "title": "Final patio setup configuration", 
                "content": "Confirmed patio area will have dedicated cannabis consumption zone with proper ventilation and separation.",
                "category_id": 1,  # venue_management
                "confidence_level": 8
            }
        ]
        
        created_count = 0
        newer_time = datetime.now()  # Current time as "newer"
        
        for item in newer_items:
            try:
                query = """
                    INSERT INTO planning_items (
                        category_id, title, content, source_id, extraction_session_id,
                        confidence_level, status, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id
                """
                
                item_id = await pool.fetchval(
                    query,
                    item['category_id'],
                    item['title'],
                    item['content'],
                    latest_session['source_id'],
                    latest_session['id'],
                    item['confidence_level'],
                    'approved',
                    newer_time + timedelta(minutes=created_count * 2)
                )
                
                created_count += 1
                print(f"Created newer item {item_id}: {item['title']}")
                
            except Exception as e:
                print(f"Failed to create item: {e}")
                continue
                
        print(f"\nCreated {created_count} newer test planning items")
        
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(create_newer_test_items())