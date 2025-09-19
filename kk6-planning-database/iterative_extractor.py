#!/usr/bin/env python3
"""
Iterative Category-by-Category Extraction Pipeline
Uses vector search to find relevant chunks, then applies professional prompts for each category.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import asyncpg
import httpx
from pydantic import BaseModel

from embedding_service import EmbeddingService
from category_prompts import CategoryPrompts

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
OPENROUTER_MODEL = env_config.get('OPENROUTER_MODEL', 'openrouter/sonoma-sky-alpha')
DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

class ExtractionResult(BaseModel):
    """Model for category extraction results."""
    category_id: int
    category_name: str
    chunk_ids: List[int]
    extracted_items: List[Dict[str, Any]]
    relevance_scores: List[float]
    processing_time_ms: int
    confidence_avg: float

class IterativeExtractor:
    """Advanced extraction system using category-specific prompts and vector search."""
    
    def __init__(self):
        self.db_pool = None
        self.embedding_service = None
        self.openrouter_client = None
        self.categories = []
        
    async def initialize(self):
        """Initialize all services and load categories."""
        self.db_pool = await asyncpg.create_pool(DATABASE_URL)
        self.embedding_service = EmbeddingService()
        await self.embedding_service.initialize()
        self.openrouter_client = httpx.AsyncClient(timeout=60.0)
        
        # Load categories from database
        await self._load_categories()
        
    async def _load_categories(self):
        """Load all categories from database."""
        query = "SELECT id, name, description FROM categories ORDER BY id"
        self.categories = await self.db_pool.fetch(query)
        logger.info(f"Loaded {len(self.categories)} categories for extraction")
        
    def _get_extraction_schema(self) -> Dict[str, Any]:
        """Get JSON schema for structured extraction outputs."""
        return {
            "name": "extraction_results",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "extracted_items": {
                        "type": "array",
                        "description": "List of extracted planning items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category_name": {
                                    "type": "string",
                                    "description": "Category name for this item"
                                },
                                "item_key": {
                                    "type": "string",
                                    "description": "Unique identifier key for the item"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Brief descriptive title"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Full context and details from transcript"
                                },
                                "value_text": {
                                    "type": "string",
                                    "description": "Specific text value or detail"
                                },
                                "value_numeric": {
                                    "type": ["number", "null"],
                                    "description": "Numeric value (cost, quantity) if mentioned"
                                },
                                "confidence_level": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 10,
                                    "description": "Confidence level 1-10"
                                },
                                "priority_level": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 5,
                                    "description": "Priority level 1-5"
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Relevant tags for categorization"
                                }
                            },
                            "required": ["category_name", "title", "content", "confidence_level", "tags"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["extracted_items"],
                "additionalProperties": False
            }
        }

    async def _call_openrouter(self, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API with structured outputs for guaranteed valid JSON."""
        try:
            response = await self.openrouter_client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "max_tokens": 3000,  # Increased for structured outputs
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": self._get_extraction_schema()
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse the guaranteed valid JSON response
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"API Error Details: {error_detail}")
                except:
                    logger.error(f"API Response Text: {e.response.text}")
            raise
            
    def _parse_extraction_response(self, response_data: Dict[str, Any], category_name: str) -> List[Dict[str, Any]]:
        """Extract items from structured JSON response."""
        try:
            extracted_items = response_data.get('extracted_items', [])
            logger.info(f"Structured response for {category_name}: {len(extracted_items)} items extracted")
            return extracted_items
            
        except Exception as e:
            logger.error(f"Failed to parse structured response for {category_name}: {e}")
            return []
            
    async def extract_category(
        self, 
        category: Dict[str, Any], 
        source_id: int, 
        relevance_threshold: float = 0.4
    ) -> ExtractionResult:
        """Extract items for a single category using vector search and professional prompts."""
        
        start_time = datetime.now()
        category_id = category['id']
        category_name = category['name']
        
        logger.info(f"🔍 Extracting category: {category_name}")
        
        try:
            # 1. Find ALL relevant chunks for this category using vector search with threshold
            relevant_chunks = await self.embedding_service.find_relevant_chunks_for_category(
                category_id, source_id, threshold=relevance_threshold
            )
            
            if not relevant_chunks:
                logger.info(f"  No relevant chunks found for {category_name}")
                return ExtractionResult(
                    category_id=category_id,
                    category_name=category_name,
                    chunk_ids=[],
                    extracted_items=[],
                    relevance_scores=[],
                    processing_time_ms=0,
                    confidence_avg=0.0
                )
            
            # 2. Extract chunk content for prompting
            chunk_contents = [chunk['content'] for chunk in relevant_chunks]
            chunk_ids = [chunk['chunk_id'] for chunk in relevant_chunks]
            relevance_scores = [chunk['relevance_score'] for chunk in relevant_chunks]
            
            logger.info(f"  Found {len(relevant_chunks)} relevant chunks (avg relevance: {sum(relevance_scores)/len(relevance_scores):.3f})")
            
            # 3. Generate category-specific professional prompt
            specialist_prompt = CategoryPrompts.get_category_prompt(category_name, chunk_contents)
            
            # 4. Call OpenRouter with specialist prompt
            response = await self._call_openrouter(specialist_prompt)
            
            # 5. Parse extraction results
            extracted_items = self._parse_extraction_response(response, category_name)
            
            # 6. Calculate metrics
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            confidence_avg = sum(item.get('confidence_level', 5) for item in extracted_items) / len(extracted_items) if extracted_items else 0.0
            
            logger.info(f"  ✅ Extracted {len(extracted_items)} items (avg confidence: {confidence_avg:.1f})")
            
            return ExtractionResult(
                category_id=category_id,
                category_name=category_name,
                chunk_ids=chunk_ids,
                extracted_items=extracted_items,
                relevance_scores=relevance_scores,
                processing_time_ms=processing_time,
                confidence_avg=confidence_avg
            )
            
        except Exception as e:
            logger.error(f"  ❌ Failed to extract {category_name}: {e}")
            return ExtractionResult(
                category_id=category_id,
                category_name=category_name,
                chunk_ids=[],
                extracted_items=[],
                relevance_scores=[],
                processing_time_ms=0,
                confidence_avg=0.0
            )
            
    async def save_extraction_results(
        self, 
        source_id: int, 
        extraction_results: List[ExtractionResult],
        start_time: datetime
    ) -> int:
        """Save all extraction results to database."""
        
        # Create extraction session
        session_query = """
            INSERT INTO extraction_sessions (
                source_id, extraction_method, extracted_by, session_notes, 
                categories_processed, started_at, completed_at, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        
        categories_processed = [result.category_name for result in extraction_results]
        total_items = sum(len(result.extracted_items) for result in extraction_results)
        
        session_row = await self.db_pool.fetchrow(
            session_query,
            source_id,
            'iterative_category_extraction',
            'iterative_extractor',
            f"Processed {len(categories_processed)} categories, extracted {total_items} items",
            categories_processed,
            start_time,
            datetime.now(),
            'completed'
        )
        session_id = session_row['id']
        
        # Save raw extraction results
        saved_count = 0
        for result in extraction_results:
            if not result.extracted_items:
                continue
                
            for item in result.extracted_items:
                try:
                    # Save to extraction_results table (raw data before deduplication)
                    raw_result_query = """
                        INSERT INTO extraction_results (
                            extraction_session_id, category_id, chunk_ids, raw_result,
                            confidence_score, relevance_score, processing_time_ms
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """
                    
                    avg_relevance = sum(result.relevance_scores) / len(result.relevance_scores) if result.relevance_scores else 0.0
                    
                    await self.db_pool.execute(
                        raw_result_query,
                        session_id,
                        result.category_id,
                        result.chunk_ids,
                        json.dumps(item),
                        item.get('confidence_level', 5) / 10.0,  # Convert to 0-1 scale
                        avg_relevance,
                        result.processing_time_ms
                    )
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save extraction result: {e}")
                    continue
                    
        logger.info(f"💾 Saved {saved_count} raw extraction results")
        return session_id
        
    async def process_transcript_iteratively(self, transcript_path: str) -> Dict[str, Any]:
        """Complete iterative extraction pipeline for a transcript."""
        
        start_time = datetime.now()
        logger.info(f"🚀 Starting iterative extraction: {Path(transcript_path).name}")
        
        # 1. First, ensure transcript is embedded
        logger.info("📊 Processing transcript with embeddings...")
        transcript_result = await self.embedding_service.process_transcript_file(transcript_path)
        source_id = transcript_result['source_id']
        
        # 2. Process each category iteratively
        logger.info(f"🔄 Processing {len(self.categories)} categories iteratively...")
        extraction_results = []
        
        for i, category in enumerate(self.categories, 1):
            logger.info(f"[{i}/{len(self.categories)}] Processing: {category['name']}")
            
            result = await self.extract_category(category, source_id)
            extraction_results.append(result)
            
            # Small delay to be nice to the API
            await asyncio.sleep(0.5)
            
        # 3. Save all results
        session_id = await self.save_extraction_results(source_id, extraction_results, start_time)
        
        # 4. Generate summary
        total_items = sum(len(result.extracted_items) for result in extraction_results)
        categories_with_results = sum(1 for result in extraction_results if result.extracted_items)
        avg_confidence = sum(result.confidence_avg for result in extraction_results if result.confidence_avg) / max(1, categories_with_results)
        
        summary = {
            "source_id": source_id,
            "session_id": session_id,
            "transcript_file": Path(transcript_path).name,
            "categories_processed": len(self.categories),
            "categories_with_results": categories_with_results,
            "total_items_extracted": total_items,
            "average_confidence": avg_confidence,
            "chunk_stats": transcript_result,
            "extraction_results": extraction_results
        }
        
        logger.info(f"✅ Iterative extraction complete!")
        logger.info(f"📊 Results: {total_items} items from {categories_with_results}/{len(self.categories)} categories")
        logger.info(f"📈 Average confidence: {avg_confidence:.1f}/10")
        
        return summary
        
    async def close(self):
        """Clean up resources."""
        if self.embedding_service:
            await self.embedding_service.close()
        if self.openrouter_client:
            await self.openrouter_client.aclose()
        if self.db_pool:
            await self.db_pool.close()

async def test_iterative_extraction():
    """Test the iterative extraction system."""
    extractor = IterativeExtractor()
    
    try:
        await extractor.initialize()
        
        # Test with first transcript in ingest folder
        ingest_folder = Path("./ingest")
        transcript_files = list(ingest_folder.glob("*.txt")) if ingest_folder.exists() else []
        
        if transcript_files:
            test_file = transcript_files[0]
            logger.info(f"🧪 Testing with: {test_file.name}")
            
            result = await extractor.process_transcript_iteratively(str(test_file))
            
            print(f"\n🎯 ITERATIVE EXTRACTION TEST RESULTS:")
            print(f"📁 File: {result['transcript_file']}")
            print(f"📊 Categories processed: {result['categories_processed']}")
            print(f"✅ Categories with results: {result['categories_with_results']}")
            print(f"📋 Total items extracted: {result['total_items_extracted']}")
            print(f"📈 Average confidence: {result['average_confidence']:.1f}/10")
            
            print(f"\n📋 Results by Category:")
            for extraction_result in result['extraction_results']:
                if extraction_result.extracted_items:
                    print(f"  {extraction_result.category_name}: {len(extraction_result.extracted_items)} items")
                    for item in extraction_result.extracted_items[:2]:  # Show first 2 items
                        print(f"    • {item.get('title', 'No title')} (confidence: {item.get('confidence_level', 0)})")
                        
        else:
            print("❌ No transcript files found in ./ingest/")
            
    finally:
        await extractor.close()

if __name__ == "__main__":
    asyncio.run(test_iterative_extraction())