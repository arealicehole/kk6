#!/usr/bin/env python3
"""
KK6 Extraction Deduplication Service
Analyzes extracted items across categories to identify duplicates and overlaps.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path

import asyncpg
import numpy as np
import httpx
from difflib import SequenceMatcher
from pydantic import BaseModel

from embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

# Load configuration
def load_env_config():
    """Load configuration from .env file."""
    env_path = Path("../.env")
    config = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    return config

env_config = load_env_config()
OPENROUTER_API_KEY = env_config.get('OPENROUTER_API_KEY', '')
OPENROUTER_MODEL = env_config.get('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

@dataclass
class ExtractedItem:
    """Represents a single extracted planning item."""
    result_id: int
    session_id: int
    category_id: int
    category_name: str
    content: Dict[str, Any]
    confidence_score: float
    relevance_score: float
    chunk_ids: List[int]

@dataclass
class DuplicateGroup:
    """Represents a group of potentially duplicate items."""
    primary_item: ExtractedItem
    duplicates: List[ExtractedItem]
    similarity_scores: List[float]
    merge_suggestion: Dict[str, Any]

class DeduplicationService:
    """Service for identifying and managing duplicate extracted items."""
    
    def __init__(self):
        self.db_pool = None
        self.embedding_service = None
        
    async def initialize(self):
        """Initialize database connection and embedding service."""
        self.db_pool = await asyncpg.create_pool(DATABASE_URL)
        self.embedding_service = EmbeddingService()
        await self.embedding_service.initialize()
        
    async def get_extraction_results(self, session_id: int) -> List[ExtractedItem]:
        """Get all extraction results from a session."""
        query = """
            SELECT 
                er.id as result_id,
                er.extraction_session_id as session_id,
                er.category_id,
                c.name as category_name,
                er.raw_result,
                er.confidence_score,
                er.relevance_score,
                er.chunk_ids
            FROM extraction_results er
            JOIN categories c ON er.category_id = c.id
            WHERE er.extraction_session_id = $1
            ORDER BY er.category_id, er.confidence_score DESC
        """
        
        rows = await self.db_pool.fetch(query, session_id)
        items = []
        
        for row in rows:
            try:
                content = json.loads(row['raw_result'])
                items.append(ExtractedItem(
                    result_id=row['result_id'],
                    session_id=row['session_id'],
                    category_id=row['category_id'],
                    category_name=row['category_name'],
                    content=content,
                    confidence_score=row['confidence_score'],
                    relevance_score=row['relevance_score'],
                    chunk_ids=row['chunk_ids'] or []
                ))
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse result {row['result_id']}: {e}")
                continue
                
        logger.info(f"Retrieved {len(items)} extraction results from session {session_id}")
        return items
        
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using sequence matching."""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
    async def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using embeddings."""
        try:
            embedding1 = await self.embedding_service.generate_embedding(text1)
            embedding2 = await self.embedding_service.generate_embedding(text2)
            
            # Calculate cosine similarity
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.warning(f"Failed to calculate semantic similarity: {e}")
            return 0.0
            
    def calculate_content_overlap(self, item1: ExtractedItem, item2: ExtractedItem) -> Dict[str, float]:
        """Calculate various similarity metrics between two items."""
        content1 = item1.content
        content2 = item2.content
        
        # Get text fields for comparison
        title1 = content1.get('title', '')
        title2 = content2.get('title', '')
        content_text1 = content1.get('content', '')
        content_text2 = content2.get('content', '')
        
        # Calculate similarities
        title_similarity = self.calculate_text_similarity(title1, title2)
        content_similarity = self.calculate_text_similarity(content_text1, content_text2)
        
        # Check for chunk overlap
        chunks1 = set(item1.chunk_ids)
        chunks2 = set(item2.chunk_ids)
        chunk_overlap = len(chunks1.intersection(chunks2)) / max(len(chunks1.union(chunks2)), 1)
        
        # Tag overlap
        tags1 = set(content1.get('tags', []))
        tags2 = set(content2.get('tags', []))
        tag_overlap = len(tags1.intersection(tags2)) / max(len(tags1.union(tags2)), 1)
        
        return {
            'title_similarity': title_similarity,
            'content_similarity': content_similarity,
            'chunk_overlap': chunk_overlap,
            'tag_overlap': tag_overlap,
            'overall_score': (title_similarity * 0.3 + content_similarity * 0.4 + 
                            chunk_overlap * 0.2 + tag_overlap * 0.1)
        }
        
    async def find_duplicate_groups(
        self, 
        items: List[ExtractedItem], 
        similarity_threshold: float = 0.6
    ) -> List[DuplicateGroup]:
        """Find groups of duplicate items across categories."""
        
        duplicate_groups = []
        processed_items = set()
        
        for i, item1 in enumerate(items):
            if item1.result_id in processed_items:
                continue
                
            # Find potential duplicates for this item
            duplicates = []
            similarity_scores = []
            
            for j, item2 in enumerate(items):
                if i == j or item2.result_id in processed_items:
                    continue
                    
                # Skip items from the same category (not really duplicates)
                if item1.category_id == item2.category_id:
                    continue
                    
                # Calculate similarity
                overlap_metrics = self.calculate_content_overlap(item1, item2)
                overall_similarity = overlap_metrics['overall_score']
                
                if overall_similarity >= similarity_threshold:
                    duplicates.append(item2)
                    similarity_scores.append(overall_similarity)
                    
            if duplicates:
                # Create merge suggestion
                merge_suggestion = await self._create_merge_suggestion(item1, duplicates)
                
                duplicate_group = DuplicateGroup(
                    primary_item=item1,
                    duplicates=duplicates,
                    similarity_scores=similarity_scores,
                    merge_suggestion=merge_suggestion
                )
                duplicate_groups.append(duplicate_group)
                
                # Mark all items in this group as processed
                processed_items.add(item1.result_id)
                for dup in duplicates:
                    processed_items.add(dup.result_id)
                    
        logger.info(f"Found {len(duplicate_groups)} duplicate groups with {similarity_threshold} threshold")
        return duplicate_groups
        
    async def _create_merge_suggestion(
        self, 
        primary: ExtractedItem, 
        duplicates: List[ExtractedItem]
    ) -> Dict[str, Any]:
        """Create an LLM-powered intelligent merge suggestion for duplicate items."""
        
        all_items = [primary] + duplicates
        
        # Try LLM-based intelligent merging first
        try:
            llm_suggestion = await self._create_llm_merge_suggestion(all_items)
            if llm_suggestion:
                return llm_suggestion
        except Exception as e:
            logger.warning(f"LLM merge failed, falling back to basic merge: {e}")
        
        # Fallback to basic merging if LLM fails
        return self._create_basic_merge_suggestion(all_items)
    
    async def _create_llm_merge_suggestion(self, items: List[ExtractedItem]) -> Dict[str, Any]:
        """Use LLM to intelligently merge duplicate items."""
        
        if not OPENROUTER_API_KEY:
            logger.warning("No OpenRouter API key configured, skipping LLM merge")
            return None
            
        # Prepare the context for the LLM
        items_context = []
        for i, item in enumerate(items):
            content = item.content
            item_text = f"""
Item {i+1} (from {item.category_name}):
- Title: {content.get('title', 'No title')}
- Description: {content.get('description', content.get('content', 'No description'))}
- Tags: {', '.join(content.get('tags', []))}
- Confidence: {item.confidence_score:.2f}
"""
            items_context.append(item_text.strip())
        
        context = "\n\n".join(items_context)
        categories = [item.category_name for item in items]
        
        prompt = f"""You are an expert event planner analyzing KK6 (Kanna Kickback 6) planning items for intelligent merging.

Below are {len(items)} similar planning items that appear to be duplicates or overlapping concepts from different planning categories. Your job is to create a single, comprehensive merged item that captures the best aspects of all items while eliminating redundancy.

ITEMS TO MERGE:
{context}

INSTRUCTIONS:
1. Create a single, clear title that encompasses the core concept
2. Write a comprehensive description that merges key information from all items
3. Select the most relevant tags from all items
4. Use the highest confidence score among the items
5. Maintain all important details while eliminating redundancy

OUTPUT FORMAT (JSON):
{{
  "title": "Clear, comprehensive title",
  "description": "Detailed description combining key insights from all items",
  "tags": ["relevant", "tags", "from", "all", "items"],
  "confidence_level": 8,
  "source_categories": {categories},
  "merge_rationale": "Brief explanation of why these items were merged and what the result represents"
}}

Generate the merged item:"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                merged_suggestion = json.loads(json_str)
                
                # Ensure required fields and add metadata
                merged_suggestion['merge_type'] = 'llm_intelligent_merge'
                merged_suggestion['source_categories'] = categories
                
                logger.info(f"✅ LLM successfully merged {len(items)} duplicate items")
                return merged_suggestion
            else:
                logger.error("Could not extract JSON from LLM response")
                return None
    
    def _create_basic_merge_suggestion(self, items: List[ExtractedItem]) -> Dict[str, Any]:
        """Fallback basic merging logic."""
        
        # Combine titles (use the longest/most descriptive)
        titles = [item.content.get('title', '') for item in items]
        merged_title = max(titles, key=len) if titles else ''
        
        # Combine descriptions (merge unique parts)
        descriptions = [
            item.content.get('description', item.content.get('content', '')) 
            for item in items
        ]
        merged_description = ' | '.join(set(filter(None, descriptions)))
        
        # Combine tags
        all_tags = []
        for item in items:
            all_tags.extend(item.content.get('tags', []))
        merged_tags = list(set(all_tags))
        
        # Use highest confidence
        max_confidence = max(item.confidence_score for item in items)
        
        # Combine categories
        categories = [item.category_name for item in items]
        
        return {
            'title': merged_title,
            'description': merged_description,
            'tags': merged_tags,
            'confidence_level': max_confidence * 10,  # Convert back to 1-10 scale
            'source_categories': categories,
            'merge_type': 'basic_fallback_merge'
        }
        
    async def analyze_session_duplicates(self, session_id: int) -> Dict[str, Any]:
        """Complete deduplication analysis for an extraction session."""
        
        logger.info(f"🔍 Starting deduplication analysis for session {session_id}")
        
        # Get all extraction results
        items = await self.get_extraction_results(session_id)
        
        if not items:
            return {
                'session_id': session_id,
                'items_by_category': {},
                'duplicate_groups': [],
                'unique_items': [],
                'summary': {
                    'session_id': session_id,
                    'total_items': 0,
                    'duplicate_groups': 0,
                    'total_duplicates': 0,
                    'unique_items': 0,
                    'reduction_percentage': 0
                }
            }
            
        # Find duplicate groups
        duplicate_groups = await self.find_duplicate_groups(items)
        
        # Identify unique items (not in any duplicate group)
        items_in_groups = set()
        for group in duplicate_groups:
            items_in_groups.add(group.primary_item.result_id)
            for dup in group.duplicates:
                items_in_groups.add(dup.result_id)
                
        unique_items = [item for item in items if item.result_id not in items_in_groups]
        
        # Generate summary
        total_duplicates = sum(len(group.duplicates) for group in duplicate_groups)
        
        summary = {
            'session_id': session_id,
            'total_items': len(items),
            'duplicate_groups': len(duplicate_groups),
            'total_duplicates': total_duplicates,
            'unique_items': len(unique_items),
            'reduction_percentage': (total_duplicates / len(items) * 100) if items else 0
        }
        
        logger.info(f"📊 Deduplication complete: {len(items)} → {len(unique_items) + len(duplicate_groups)} items")
        logger.info(f"🎯 Found {len(duplicate_groups)} duplicate groups, {total_duplicates} duplicates removed")
        
        return {
            'session_id': session_id,
            'items_by_category': self._group_items_by_category(items),
            'duplicate_groups': duplicate_groups,
            'unique_items': unique_items,
            'summary': summary
        }
        
    def _group_items_by_category(self, items: List[ExtractedItem]) -> Dict[str, List[ExtractedItem]]:
        """Group items by category for display."""
        groups = defaultdict(list)
        for item in items:
            groups[item.category_name].append(item)
        return dict(groups)
        
    async def close(self):
        """Clean up resources."""
        if self.embedding_service:
            await self.embedding_service.close()
        if self.db_pool:
            await self.db_pool.close()

async def test_deduplication():
    """Test the deduplication service."""
    service = DeduplicationService()
    
    try:
        await service.initialize()
        
        # Get the latest extraction session
        latest_session = await service.db_pool.fetchrow(
            "SELECT id FROM extraction_sessions ORDER BY completed_at DESC LIMIT 1"
        )
        
        if latest_session:
            session_id = latest_session['id']
            print(f"🧪 Testing deduplication on session {session_id}")
            
            results = await service.analyze_session_duplicates(session_id)
            
            print(f"\n🎯 DEDUPLICATION TEST RESULTS:")
            print(f"📊 Total items: {results['summary']['total_items']}")
            print(f"🔄 Duplicate groups: {results['summary']['duplicate_groups']}")
            print(f"✨ Unique items: {results['summary']['unique_items']}")
            print(f"📉 Reduction: {results['summary']['reduction_percentage']:.1f}%")
            
            # Show duplicate groups
            if results['duplicate_groups']:
                print(f"\n🔍 Duplicate Groups Found:")
                for i, group in enumerate(results['duplicate_groups'], 1):
                    print(f"\n  Group {i}:")
                    print(f"    Primary: {group.primary_item.content.get('title', 'No title')} ({group.primary_item.category_name})")
                    for j, dup in enumerate(group.duplicates):
                        score = group.similarity_scores[j]
                        print(f"    Duplicate: {dup.content.get('title', 'No title')} ({dup.category_name}) - {score:.3f} similarity")
                    print(f"    Suggested merge: {group.merge_suggestion.get('title', 'No suggestion')}")
        else:
            print("❌ No extraction sessions found")
            
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(test_deduplication())