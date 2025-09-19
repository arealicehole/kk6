"""Repository for transcript database operations."""

import json
import logging
from typing import Optional

import numpy as np

from .connection import DatabaseManager, get_db_manager
from .models import TranscriptRecord

logger = logging.getLogger(__name__)


class TranscriptRepository:
    """Repository for transcript database operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        """Initialize repository.
        
        Args:
            db_manager: Database manager instance (uses global if None)
        """
        self.db = db_manager or get_db_manager()
    
    async def create_transcript(self, transcript: TranscriptRecord) -> TranscriptRecord:
        """Create a new transcript record.
        
        Args:
            transcript: Transcript data to insert
            
        Returns:
            Created transcript with populated ID and timestamps
            
        Raises:
            DatabaseError: If creation fails
        """
        # Convert embedding to string format for PostgreSQL
        embedding_str = None
        if transcript.embedding:
            embedding_str = f"[{','.join(map(str, transcript.embedding))}]"
        
        query = """
            INSERT INTO transcripts (
                filename, content, mentions_kickback, confidence_score, 
                analysis_notes, embedding, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6::vector, $7)
            RETURNING id, created_at, updated_at
        """
        
        try:
            row = await self.db.fetch_one(
                query,
                transcript.filename,
                transcript.content,
                transcript.mentions_kickback,
                transcript.confidence_score,
                transcript.analysis_notes,
                embedding_str,
                json.dumps(transcript.metadata),
            )
            
            if not row:
                raise ValueError("Failed to create transcript record")
            
            # Update the transcript with returned values
            transcript.id = row["id"]
            transcript.created_at = row["created_at"]
            transcript.updated_at = row["updated_at"]
            
            logger.info(f"Created transcript record with ID {transcript.id}")
            return transcript
            
        except Exception as e:
            logger.error(f"Failed to create transcript: {e}")
            raise
    
    async def get_transcript_by_id(self, transcript_id: int) -> Optional[TranscriptRecord]:
        """Get transcript by ID.
        
        Args:
            transcript_id: Transcript ID
            
        Returns:
            Transcript record or None if not found
        """
        query = """
            SELECT id, filename, content, mentions_kickback, confidence_score,
                   analysis_notes, embedding, metadata, created_at, updated_at
            FROM transcripts WHERE id = $1
        """
        
        row = await self.db.fetch_one(query, transcript_id)
        if not row:
            return None
        
        return self._row_to_transcript(row)
    
    async def get_transcript_by_filename(self, filename: str) -> Optional[TranscriptRecord]:
        """Get transcript by filename.
        
        Args:
            filename: Transcript filename
            
        Returns:
            Transcript record or None if not found
        """
        query = """
            SELECT id, filename, content, mentions_kickback, confidence_score,
                   analysis_notes, embedding, metadata, created_at, updated_at
            FROM transcripts WHERE filename = $1
        """
        
        row = await self.db.fetch_one(query, filename)
        if not row:
            return None
        
        return self._row_to_transcript(row)
    
    async def list_transcripts(
        self, 
        mentions_kickback: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[TranscriptRecord]:
        """List transcript records with optional filtering.
        
        Args:
            mentions_kickback: Filter by kickback mentions (None = all)
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of transcript records
        """
        conditions = []
        params = []
        param_count = 0
        
        if mentions_kickback is not None:
            param_count += 1
            conditions.append(f"mentions_kickback = ${param_count}")
            params.append(mentions_kickback)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        
        limit_clause = ""
        if limit is not None:
            param_count += 1
            limit_clause = f" LIMIT ${param_count}"
            params.append(limit)
        
        param_count += 1
        offset_clause = f" OFFSET ${param_count}"
        params.append(offset)
        
        query = f"""
            SELECT id, filename, content, mentions_kickback, confidence_score,
                   analysis_notes, embedding, metadata, created_at, updated_at
            FROM transcripts{where_clause}
            ORDER BY created_at DESC{limit_clause}{offset_clause}
        """
        
        rows = await self.db.fetch_all(query, *params)
        return [self._row_to_transcript(row) for row in rows]
    
    async def count_transcripts(self, mentions_kickback: Optional[bool] = None) -> int:
        """Count transcript records.
        
        Args:
            mentions_kickback: Filter by kickback mentions (None = all)
            
        Returns:
            Total count of matching records
        """
        if mentions_kickback is not None:
            query = "SELECT COUNT(*) as count FROM transcripts WHERE mentions_kickback = $1"
            row = await self.db.fetch_one(query, mentions_kickback)
        else:
            query = "SELECT COUNT(*) as count FROM transcripts"
            row = await self.db.fetch_one(query)
        
        return row["count"] if row else 0
    
    async def update_transcript(self, transcript: TranscriptRecord) -> TranscriptRecord:
        """Update an existing transcript record.
        
        Args:
            transcript: Transcript data with ID set
            
        Returns:
            Updated transcript record
            
        Raises:
            ValueError: If transcript ID is not set
            DatabaseError: If update fails
        """
        if not transcript.id:
            raise ValueError("Transcript ID must be set for updates")
        
        # Convert embedding to string format for PostgreSQL
        embedding_str = None
        if transcript.embedding:
            embedding_str = f"[{','.join(map(str, transcript.embedding))}]"
        
        query = """
            UPDATE transcripts SET
                filename = $2, content = $3, mentions_kickback = $4,
                confidence_score = $5, analysis_notes = $6, 
                embedding = $7::vector, metadata = $8,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING updated_at
        """
        
        try:
            row = await self.db.fetch_one(
                query,
                transcript.id,
                transcript.filename,
                transcript.content,
                transcript.mentions_kickback,
                transcript.confidence_score,
                transcript.analysis_notes,
                embedding_str,
                json.dumps(transcript.metadata),
            )
            
            if not row:
                raise ValueError(f"Transcript with ID {transcript.id} not found")
            
            transcript.updated_at = row["updated_at"]
            
            logger.info(f"Updated transcript record with ID {transcript.id}")
            return transcript
            
        except Exception as e:
            logger.error(f"Failed to update transcript: {e}")
            raise
    
    async def delete_transcript(self, transcript_id: int) -> bool:
        """Delete a transcript record.
        
        Args:
            transcript_id: Transcript ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM transcripts WHERE id = $1"
        
        try:
            result = await self.db.execute_query(query, transcript_id)
            logger.info(f"Deleted transcript record with ID {transcript_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete transcript {transcript_id}: {e}")
            return False
    
    async def find_similar_transcripts(
        self, 
        embedding: list[float], 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> list[tuple[TranscriptRecord, float]]:
        """Find transcripts similar to the given embedding.
        
        Args:
            embedding: Vector embedding to search for
            limit: Maximum number of results
            similarity_threshold: Minimum cosine similarity score
            
        Returns:
            List of (transcript, similarity_score) tuples
        """
        embedding_str = f"[{','.join(map(str, embedding))}]"
        
        query = """
            SELECT id, filename, content, mentions_kickback, confidence_score,
                   analysis_notes, embedding, metadata, created_at, updated_at,
                   1 - (embedding <=> $1::vector) as similarity
            FROM transcripts 
            WHERE embedding IS NOT NULL
              AND 1 - (embedding <=> $1::vector) >= $2
            ORDER BY embedding <=> $1::vector
            LIMIT $3
        """
        
        rows = await self.db.fetch_all(query, embedding_str, similarity_threshold, limit)
        
        results = []
        for row in rows:
            transcript = self._row_to_transcript(row)
            similarity = float(row["similarity"])
            results.append((transcript, similarity))
        
        return results
    
    def _row_to_transcript(self, row: dict) -> TranscriptRecord:
        """Convert database row to TranscriptRecord.
        
        Args:
            row: Database row as dict
            
        Returns:
            TranscriptRecord instance
        """
        # Parse embedding from string format
        embedding = None
        if row.get("embedding"):
            try:
                # Convert PostgreSQL vector format to list
                embedding_str = str(row["embedding"])
                if embedding_str.startswith("[") and embedding_str.endswith("]"):
                    embedding_str = embedding_str[1:-1]  # Remove brackets
                    embedding = [float(x.strip()) for x in embedding_str.split(",")]
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse embedding: {e}")
        
        # Parse metadata JSON
        metadata = {}
        if row.get("metadata"):
            try:
                metadata = json.loads(row["metadata"])
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to parse metadata: {e}")
        
        return TranscriptRecord(
            id=row["id"],
            filename=row["filename"],
            content=row["content"],
            mentions_kickback=row["mentions_kickback"],
            confidence_score=row["confidence_score"],
            analysis_notes=row["analysis_notes"],
            embedding=embedding,
            metadata=metadata,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )