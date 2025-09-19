"""Database connection management."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import asyncpg
from asyncpg import Connection, Pool

from ..utils import get_settings

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Database operation error."""
    pass


class DatabaseManager:
    """Manages PostgreSQL database connections."""
    
    def __init__(self) -> None:
        """Initialize database manager."""
        self.settings = get_settings()
        self.pool: Optional[Pool] = None
    
    async def initialize(self) -> None:
        """Initialize the connection pool."""
        if self.pool is not None:
            return
        
        try:
            logger.info("Initializing database connection pool")
            self.pool = await asyncpg.create_pool(
                self.settings.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
            logger.info("Database connection pool initialized")
            
            # Test the connection
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                logger.info("Database connection test successful")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}") from e
    
    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool is not None:
            logger.info("Closing database connection pool")
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Connection, None]:
        """Get a database connection from the pool.
        
        Yields:
            Database connection
            
        Raises:
            DatabaseError: If pool is not initialized or connection fails
        """
        if self.pool is None:
            await self.initialize()
        
        if self.pool is None:
            raise DatabaseError("Database pool is not initialized")
        
        try:
            async with self.pool.acquire() as connection:
                yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Database connection failed: {e}") from e
    
    async def execute_query(
        self, 
        query: str, 
        *args, 
        fetch: bool = False
    ) -> Optional[list]:
        """Execute a database query.
        
        Args:
            query: SQL query to execute
            *args: Query parameters
            fetch: Whether to fetch and return results
            
        Returns:
            Query results if fetch=True, otherwise None
            
        Raises:
            DatabaseError: If query execution fails
        """
        try:
            async with self.get_connection() as conn:
                if fetch:
                    return await conn.fetch(query, *args)
                else:
                    await conn.execute(query, *args)
                    return None
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Args: {args}")
            raise DatabaseError(f"Query execution failed: {e}") from e
    
    async def fetch_one(self, query: str, *args) -> Optional[dict]:
        """Fetch a single row from the database.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            Single row as dict or None if not found
        """
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(query, *args)
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Fetch one failed: {e}")
            raise DatabaseError(f"Fetch one failed: {e}") from e
    
    async def fetch_all(self, query: str, *args) -> list[dict]:
        """Fetch all rows from the database.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            List of rows as dicts
        """
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Fetch all failed: {e}")
            raise DatabaseError(f"Fetch all failed: {e}") from e


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager