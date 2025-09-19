#!/usr/bin/env python3
"""Setup script for KK6 Planning Database."""

import asyncio
import asyncpg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/postgres"
PLANNING_DB_NAME = "kk6_planning"

async def setup_planning_database():
    """Create and setup the KK6 planning database."""
    
    # Connect to PostgreSQL server
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Check if database exists
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", 
            PLANNING_DB_NAME
        )
        
        if result:
            logger.info(f"Database '{PLANNING_DB_NAME}' already exists")
        else:
            # Create database
            await conn.execute(f'CREATE DATABASE "{PLANNING_DB_NAME}"')
            logger.info(f"Created database '{PLANNING_DB_NAME}'")
        
    finally:
        await conn.close()
    
    # Connect to the planning database and run schema
    planning_db_url = f"postgresql://postgres:postgres@localhost:55432/{PLANNING_DB_NAME}"
    planning_conn = await asyncpg.connect(planning_db_url)
    
    try:
        # Read and execute schema
        with open('kk6_planning_db_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        await planning_conn.execute(schema_sql)
        logger.info("Database schema created successfully")
        
        # Verify tables were created
        tables = await planning_conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        logger.info(f"Created tables: {[table['table_name'] for table in tables]}")
        
        # Check categories were populated
        category_count = await planning_conn.fetchval("SELECT COUNT(*) FROM categories")
        logger.info(f"Populated {category_count} categories")
        
    finally:
        await planning_conn.close()
    
    logger.info("KK6 Planning Database setup complete!")

if __name__ == "__main__":
    asyncio.run(setup_planning_database())