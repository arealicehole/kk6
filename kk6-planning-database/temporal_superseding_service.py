#!/usr/bin/env python3
"""
Temporal Superseding Service for KK6 Planning Items
Implements automatic temporal precedence where newer conversations can flag older items as superseded.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

import asyncpg
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

@dataclass
class PlanningItem:
    """Represents a planning item with temporal context."""
    id: int
    title: str
    content: str
    category_id: int
    source_id: int
    extraction_session_id: int
    created_at: datetime
    superseded_by: Optional[int] = None
    supersedes: List[int] = None
    confidence_level: int = 5
    embedding: Optional[List[float]] = None

@dataclass
class SupersedingCandidate:
    """Represents a potential superseding relationship."""
    newer_item: PlanningItem
    older_item: PlanningItem
    similarity_score: float
    temporal_gap_days: int
    confidence: float
    reason: str

class TemporalSupersedingService:
    """Service for detecting and managing temporal superseding relationships."""
    
    def __init__(self):
        self.db_pool = None
        
    async def initialize(self):
        """Initialize database connection."""
        self.db_pool = await asyncpg.create_pool(DATABASE_URL)
        
    async def find_superseding_candidates(
        self, 
        newer_session_id: int,
        similarity_threshold: float = 0.7,
        max_temporal_gap_days: int = 30
    ) -> List[SupersedingCandidate]:
        """
        Find items from newer sessions that potentially supersede older items.
        
        Args:
            newer_session_id: The extraction session to check for superseding items
            similarity_threshold: Minimum semantic similarity (0-1) to consider superseding
            max_temporal_gap_days: Maximum days between conversations to consider
            
        Returns:
            List of potential superseding relationships
        """
        logger.info(f"🔍 Finding superseding candidates for session {newer_session_id}")
        
        # Get items from the newer session
        newer_items = await self._get_session_items(newer_session_id)
        if not newer_items:
            logger.info("No items found in newer session")
            return []
            
        logger.info(f"Found {len(newer_items)} items in newer session")
        
        candidates = []
        
        for newer_item in newer_items:
            # Find potentially superseded older items
            older_candidates = await self._find_similar_older_items(
                newer_item, 
                similarity_threshold,
                max_temporal_gap_days
            )
            
            for older_item, similarity in older_candidates:
                # Calculate temporal gap
                temporal_gap = (newer_item.created_at - older_item.created_at).days
                
                # Calculate superseding confidence based on multiple factors
                confidence = self._calculate_superseding_confidence(
                    newer_item, older_item, similarity, temporal_gap
                )
                
                # Generate reason for superseding
                reason = self._generate_superseding_reason(
                    newer_item, older_item, similarity, temporal_gap
                )
                
                candidates.append(SupersedingCandidate(
                    newer_item=newer_item,
                    older_item=older_item,
                    similarity_score=similarity,
                    temporal_gap_days=temporal_gap,
                    confidence=confidence,
                    reason=reason
                ))
                
        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.info(f"Found {len(candidates)} superseding candidates")
        return candidates
        
    async def _get_session_items(self, session_id: int) -> List[PlanningItem]:
        """Get all planning items from a specific extraction session."""
        query = """
            SELECT 
                pi.id, pi.title, pi.content, pi.category_id, pi.source_id,
                pi.extraction_session_id, pi.created_at, pi.superseded_by,
                pi.supersedes, pi.confidence_level, pi.embedding
            FROM planning_items pi
            WHERE pi.extraction_session_id = $1
                AND pi.superseded_by IS NULL  -- Only active items
            ORDER BY pi.created_at
        """
        
        rows = await self.db_pool.fetch(query, session_id)
        
        items = []
        for row in rows:
            items.append(PlanningItem(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                category_id=row['category_id'],
                source_id=row['source_id'],
                extraction_session_id=row['extraction_session_id'],
                created_at=row['created_at'],
                superseded_by=row['superseded_by'],
                supersedes=row['supersedes'] or [],
                confidence_level=row['confidence_level'],
                embedding=self._parse_embedding(row['embedding'])
            ))
            
        return items
        
    async def _find_similar_older_items(
        self, 
        newer_item: PlanningItem, 
        similarity_threshold: float,
        max_temporal_gap_days: int
    ) -> List[Tuple[PlanningItem, float]]:
        """Find older items similar to the newer item."""
        
        if not newer_item.embedding:
            logger.warning(f"No embedding for item {newer_item.id}, skipping similarity search")
            return []
            
        # Convert embedding to PostgreSQL vector format
        embedding_str = f"[{','.join(map(str, newer_item.embedding))}]"
        
        # Find similar older items using vector search
        query = """
            SELECT 
                pi.id, pi.title, pi.content, pi.category_id, pi.source_id,
                pi.extraction_session_id, pi.created_at, pi.superseded_by,
                pi.supersedes, pi.confidence_level, pi.embedding,
                1 - (pi.embedding <=> $1::vector) as similarity
            FROM planning_items pi
            JOIN extraction_sessions es ON pi.extraction_session_id = es.id
            WHERE pi.created_at < $2  -- Must be older
                AND pi.created_at > $3  -- Within temporal window
                AND pi.superseded_by IS NULL  -- Only active items
                AND pi.embedding IS NOT NULL  -- Must have embedding
                AND pi.category_id = $4  -- Same category
                AND 1 - (pi.embedding <=> $1::vector) >= $5  -- Similarity threshold
            ORDER BY similarity DESC
            LIMIT 10
        """
        
        older_than = newer_item.created_at
        newer_than = older_than - timedelta(days=max_temporal_gap_days)
        
        rows = await self.db_pool.fetch(
            query, 
            embedding_str,
            older_than,
            newer_than,
            newer_item.category_id,
            similarity_threshold
        )
        
        similar_items = []
        for row in rows:
            older_item = PlanningItem(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                category_id=row['category_id'],
                source_id=row['source_id'],
                extraction_session_id=row['extraction_session_id'],
                created_at=row['created_at'],
                superseded_by=row['superseded_by'],
                supersedes=row['supersedes'] or [],
                confidence_level=row['confidence_level'],
                embedding=self._parse_embedding(row['embedding'])
            )
            
            similarity = float(row['similarity'])
            similar_items.append((older_item, similarity))
            
        return similar_items
        
    def _calculate_superseding_confidence(
        self, 
        newer_item: PlanningItem,
        older_item: PlanningItem,
        similarity: float,
        temporal_gap_days: int
    ) -> float:
        """Calculate confidence that newer item supersedes older item."""
        
        # Base confidence from semantic similarity
        confidence = similarity
        
        # Boost confidence for higher confidence newer items
        confidence_boost = (newer_item.confidence_level - 5) * 0.1  # -0.4 to +0.5
        confidence = min(1.0, confidence + confidence_boost)
        
        # Slightly reduce confidence for very large temporal gaps
        if temporal_gap_days > 14:
            time_penalty = (temporal_gap_days - 14) * 0.01  # 1% per day after 14 days
            confidence = max(0.1, confidence - time_penalty)
            
        # Boost confidence if newer item has more detailed content
        if len(newer_item.content) > len(older_item.content) * 1.5:
            confidence = min(1.0, confidence + 0.1)
            
        return confidence
        
    def _generate_superseding_reason(
        self,
        newer_item: PlanningItem,
        older_item: PlanningItem,
        similarity: float,
        temporal_gap_days: int
    ) -> str:
        """Generate human-readable reason for superseding relationship."""
        
        reasons = []
        
        # Semantic similarity reason
        if similarity >= 0.9:
            reasons.append(f"highly similar content ({similarity:.2f})")
        elif similarity >= 0.8:
            reasons.append(f"very similar content ({similarity:.2f})")
        else:
            reasons.append(f"similar content ({similarity:.2f})")
            
        # Temporal reason
        if temporal_gap_days <= 1:
            reasons.append("same day conversation")
        elif temporal_gap_days <= 7:
            reasons.append(f"{temporal_gap_days} days later")
        else:
            reasons.append(f"{temporal_gap_days} days later")
            
        # Content comparison
        if len(newer_item.content) > len(older_item.content) * 1.5:
            reasons.append("more detailed information")
            
        # Confidence comparison
        if newer_item.confidence_level > older_item.confidence_level:
            reasons.append("higher extraction confidence")
            
        return f"Newer item has {', '.join(reasons)}"
        
    async def apply_superseding_relationships(
        self, 
        candidates: List[SupersedingCandidate],
        confidence_threshold: float = 0.8
    ) -> int:
        """
        Apply superseding relationships for high-confidence candidates.
        
        Args:
            candidates: List of superseding candidates
            confidence_threshold: Minimum confidence to auto-apply superseding
            
        Returns:
            Number of relationships applied
        """
        applied_count = 0
        
        for candidate in candidates:
            if candidate.confidence >= confidence_threshold:
                await self._apply_superseding(candidate)
                applied_count += 1
                logger.info(
                    f"✅ Applied superseding: Item {candidate.newer_item.id} "
                    f"supersedes {candidate.older_item.id} (confidence: {candidate.confidence:.2f})"
                )
                
        return applied_count
        
    async def _apply_superseding(self, candidate: SupersedingCandidate):
        """Apply a single superseding relationship."""
        
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                # Update older item to mark it as superseded
                await conn.execute(
                    "UPDATE planning_items SET superseded_by = $1, updated_at = NOW() WHERE id = $2",
                    candidate.newer_item.id,
                    candidate.older_item.id
                )
                
                # Update newer item to record what it supersedes
                current_supersedes = candidate.newer_item.supersedes or []
                new_supersedes = current_supersedes + [candidate.older_item.id]
                
                await conn.execute(
                    "UPDATE planning_items SET supersedes = $1, updated_at = NOW() WHERE id = $2",
                    new_supersedes,
                    candidate.newer_item.id
                )
                
    def _parse_embedding(self, embedding_data) -> Optional[List[float]]:
        """Parse embedding from database format."""
        if not embedding_data:
            return None
            
        try:
            # Convert PostgreSQL vector to Python list
            if hasattr(embedding_data, '__iter__'):
                return list(embedding_data)
            else:
                # Handle string representation
                embedding_str = str(embedding_data).strip('[]')
                return [float(x) for x in embedding_str.split(',')]
        except Exception as e:
            logger.error(f"Failed to parse embedding: {e}")
            return None
            
    async def close(self):
        """Clean up resources."""
        if self.db_pool:
            await self.db_pool.close()

# Import timedelta that was missing
from datetime import timedelta

async def test_temporal_superseding():
    """Test the temporal superseding service."""
    service = TemporalSupersedingService()
    
    try:
        await service.initialize()
        
        # Get the latest extraction session
        latest_session = await service.db_pool.fetchrow(
            "SELECT id FROM extraction_sessions ORDER BY completed_at DESC LIMIT 1"
        )
        
        if latest_session:
            session_id = latest_session['id']
            
            # Find superseding candidates
            candidates = await service.find_superseding_candidates(session_id)
            
            if candidates:
                print(f"🔍 Found {len(candidates)} superseding candidates:")
                for i, candidate in enumerate(candidates, 1):
                    print(f"  {i}. Confidence: {candidate.confidence:.2f}")
                    print(f"     Newer: '{candidate.newer_item.title}'")
                    print(f"     Older: '{candidate.older_item.title}'")
                    print(f"     Reason: {candidate.reason}")
                    print()
                    
                # Apply high-confidence relationships
                applied = await service.apply_superseding_relationships(candidates)
                print(f"✅ Applied {applied} superseding relationships")
            else:
                print("No superseding candidates found")
        else:
            print("No extraction sessions found")
            
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(test_temporal_superseding())