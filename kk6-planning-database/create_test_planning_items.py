#!/usr/bin/env python3
"""
Create test planning items from extraction results for testing temporal superseding logic.
"""

import asyncio
import json
import asyncpg
from datetime import datetime, timedelta

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

async def create_test_planning_items():
    """Create test planning items from extraction results."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    try:
        # Get some extraction results to convert to planning items
        results = await pool.fetch("""
            SELECT er.id, er.extraction_session_id, er.category_id, er.raw_result,
                   er.confidence_score, es.source_id, es.completed_at
            FROM extraction_results er
            JOIN extraction_sessions es ON er.extraction_session_id = es.id
            ORDER BY es.completed_at DESC
            LIMIT 10
        """)
        
        if not results:
            print("No extraction results found")
            return
            
        created_count = 0
        
        for result in results:
            try:
                raw_data = json.loads(result['raw_result'])
                
                # Create planning item
                query = """
                    INSERT INTO planning_items (
                        category_id, title, content, source_id, extraction_session_id,
                        extraction_result_ids, confidence_level, status, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING id
                """
                
                # Create some temporal variation for testing
                created_at = result['completed_at'] + timedelta(minutes=created_count * 5)
                
                item_id = await pool.fetchval(
                    query,
                    result['category_id'],
                    raw_data.get('title', 'Test Item'),
                    raw_data.get('content', 'Test content'),
                    result['source_id'],
                    result['extraction_session_id'],
                    [result['id']],
                    raw_data.get('confidence_level', 5),
                    'approved',
                    created_at
                )
                
                created_count += 1
                print(f"Created planning item {item_id}: {raw_data.get('title', 'Test Item')[:50]}")
                
            except Exception as e:
                print(f"Failed to create item from result {result['id']}: {e}")
                continue
                
        print(f"\nCreated {created_count} test planning items")
        
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(create_test_planning_items())