#!/usr/bin/env python3
"""
KK6 Transcript Extraction Process
Extracts planning information from transcripts and populates the planning database.
"""

import json
import asyncio
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
from pathlib import Path

import asyncpg
import httpx
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

class ExtractedItem(BaseModel):
    """Model for an extracted planning item."""
    category_name: str
    item_key: Optional[str] = None
    title: str
    content: str
    value_text: Optional[str] = None
    value_numeric: Optional[float] = None
    value_date: Optional[str] = None  # Will convert to date
    value_boolean: Optional[bool] = None
    confidence_level: int
    priority_level: int = 3
    tags: List[str] = []

class TranscriptExtractor:
    """Main class for extracting planning information from transcripts."""
    
    def __init__(self):
        self.db_pool = None
        self.categories_map = {}
        
    async def initialize(self):
        """Initialize database connection and load categories."""
        self.db_pool = await asyncpg.create_pool(DATABASE_URL)
        await self._load_categories()
        
    async def _load_categories(self):
        """Load categories from database into memory."""
        query = "SELECT id, name FROM categories"
        rows = await self.db_pool.fetch(query)
        self.categories_map = {row['name'].lower(): row['id'] for row in rows}
        logger.info(f"Loaded {len(self.categories_map)} categories")
        
    async def extract_from_transcript(self, transcript_path: str) -> List[ExtractedItem]:
        """Extract planning items from a single transcript."""
        
        # Read transcript content
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
            
        # Create extraction prompt
        prompt = self._create_extraction_prompt(transcript_content)
        
        # Call Ollama for extraction
        try:
            extracted_data = await self._call_ollama(prompt)
            items = self._parse_extraction_results(extracted_data)
            logger.info(f"Extracted {len(items)} items from {transcript_path}")
            return items
        except Exception as e:
            logger.error(f"Failed to extract from {transcript_path}: {e}")
            return []
            
    def _create_extraction_prompt(self, transcript_content: str) -> str:
        """Create a structured prompt for extracting planning information."""
        
        categories_list = "\n".join([f"- {name}" for name in self.categories_map.keys()])
        
        return f"""
You are an expert event planning assistant. Extract ALL planning-relevant information from this Kanna Kickback 6 transcript.

AVAILABLE CATEGORIES:
{categories_list}

TRANSCRIPT:
{transcript_content}

EXTRACTION RULES:
1. Extract ANY information that could be useful for event planning
2. Assign each item to the most appropriate category
3. Use specific, actionable titles
4. Include confidence levels (1-10) based on how clear/certain the information is
5. Add relevant tags for easier searching
6. Extract numbers, dates, names, locations, requirements, etc.

RESPONSE FORMAT (JSON only):
{{
  "extracted_items": [
    {{
      "category_name": "exact category name from list above",
      "item_key": "unique_identifier_for_this_type_of_item",
      "title": "Clear, descriptive title",
      "content": "Full details and context from transcript",
      "value_text": "text value if applicable",
      "value_numeric": number_if_applicable,
      "value_date": "YYYY-MM-DD if date mentioned",
      "value_boolean": true_or_false_if_applicable,
      "confidence_level": 1-10,
      "priority_level": 1-5,
      "tags": ["tag1", "tag2", "tag3"]
    }}
  ]
}}

Focus on:
- Attendance numbers
- Venue details
- Food/catering plans
- Cannabis requirements
- Partnership agreements
- Budget/revenue information
- Dates and timelines
- Staffing needs
- Equipment/supplies
- Legal/compliance issues
- Marketing plans
- Risk factors

Extract everything, even if uncertain - we can verify later.
"""

    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API for text generation."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent extraction
                        "top_k": 10,
                        "top_p": 0.9
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
            
    def _parse_extraction_results(self, ollama_response: str) -> List[ExtractedItem]:
        """Parse the JSON response from Ollama into ExtractedItem objects."""
        try:
            # Try to find JSON in the response
            json_start = ollama_response.find('{')
            json_end = ollama_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.error("No JSON found in Ollama response")
                return []
                
            json_str = ollama_response[json_start:json_end]
            data = json.loads(json_str)
            
            items = []
            for item_data in data.get('extracted_items', []):
                try:
                    # Validate category exists
                    category_name = item_data.get('category_name', '').lower()
                    if category_name not in self.categories_map:
                        logger.warning(f"Unknown category: {category_name}")
                        continue
                        
                    # Convert date string to date object if present
                    date_str = item_data.get('value_date')
                    if date_str:
                        try:
                            item_data['value_date'] = date_str  # Keep as string for now
                        except:
                            item_data['value_date'] = None
                            
                    item = ExtractedItem(**item_data)
                    items.append(item)
                except Exception as e:
                    logger.error(f"Failed to parse item: {e}")
                    continue
                    
            return items
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Ollama: {e}")
            return []
            
    async def save_to_database(self, items: List[ExtractedItem], source_reference: str) -> int:
        """Save extracted items to the planning database."""
        
        # Create source record
        source_query = """
            INSERT INTO sources (type, reference, metadata)
            VALUES ($1, $2, $3)
            RETURNING id
        """
        source_row = await self.db_pool.fetchrow(
            source_query, 
            'transcript', 
            source_reference,
            json.dumps({"extracted_at": datetime.now().isoformat()})
        )
        source_id = source_row['id']
        
        # Create extraction session
        session_query = """
            INSERT INTO extraction_sessions (source_id, extraction_method, extracted_by, session_notes, completed_at, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        session_row = await self.db_pool.fetchrow(
            session_query,
            source_id,
            'llm_analysis_ollama',
            'kk6_transcript_extractor',
            f"Extracted {len(items)} items using {OLLAMA_MODEL}",
            datetime.now(),
            'completed'
        )
        session_id = session_row['id']
        
        # Insert planning items
        saved_count = 0
        for item in items:
            try:
                category_id = self.categories_map[item.category_name.lower()]
                
                # Convert date string to date object
                value_date = None
                if item.value_date:
                    try:
                        value_date = datetime.strptime(item.value_date, '%Y-%m-%d').date()
                    except:
                        pass
                
                item_query = """
                    INSERT INTO planning_items (
                        category_id, item_key, title, content, value_text, value_numeric,
                        value_date, value_boolean, confidence_level, priority_level,
                        source_id, extraction_session_id, tags
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """
                
                await self.db_pool.execute(
                    item_query,
                    category_id, item.item_key, item.title, item.content,
                    item.value_text, item.value_numeric, value_date, item.value_boolean,
                    item.confidence_level, item.priority_level,
                    source_id, session_id, item.tags
                )
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save item '{item.title}': {e}")
                continue
                
        logger.info(f"Saved {saved_count}/{len(items)} items to database")
        return saved_count
        
    async def process_transcript_folder(self, folder_path: str) -> Dict[str, int]:
        """Process all transcripts in a folder."""
        folder = Path(folder_path)
        results = {}
        
        if not folder.exists():
            logger.error(f"Folder not found: {folder_path}")
            return results
            
        # Find all transcript files
        transcript_files = list(folder.glob("*.txt"))
        logger.info(f"Found {len(transcript_files)} transcript files")
        
        for transcript_file in transcript_files:
            logger.info(f"Processing: {transcript_file.name}")
            
            try:
                items = await self.extract_from_transcript(str(transcript_file))
                if items:
                    saved_count = await self.save_to_database(items, transcript_file.name)
                    results[transcript_file.name] = saved_count
                else:
                    results[transcript_file.name] = 0
                    
            except Exception as e:
                logger.error(f"Failed to process {transcript_file.name}: {e}")
                results[transcript_file.name] = 0
                
        return results
        
    async def close(self):
        """Close database connections."""
        if self.db_pool:
            await self.db_pool.close()

async def main():
    """Main extraction process."""
    extractor = TranscriptExtractor()
    
    try:
        await extractor.initialize()
        
        # Process the transcript files that were analyzed
        transcript_folder = "../gilbert-transcripts"
        results = await extractor.process_transcript_folder(transcript_folder)
        
        # Print results
        print("\n=== EXTRACTION RESULTS ===")
        total_items = 0
        for filename, count in results.items():
            print(f"{filename}: {count} items extracted")
            total_items += count
            
        print(f"\nTotal items extracted: {total_items}")
        print("View results at: http://localhost:8090/web")
        
    finally:
        await extractor.close()

if __name__ == "__main__":
    asyncio.run(main())