#!/usr/bin/env python3
"""
Manual KK6 Transcript Extractor
Hands-on extraction process using OpenRouter API, one transcript at a time.
"""

import json
import asyncio
import logging
import os
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

# Load configuration from .env file
def load_env_config():
    """Load configuration from .env file."""
    env_path = Path("../.env")
    if not env_path.exists():
        # Try current directory
        env_path = Path(".env")
    
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
DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

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

class ManualExtractor:
    """Manual extraction system with OpenRouter API."""
    
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
        
    def _create_extraction_prompt(self, transcript_content: str) -> str:
        """Create a structured prompt for extracting planning information."""
        
        categories_list = "\n".join([f"- {name.title()}" for name in self.categories_map.keys()])
        
        return f"""You are an expert event planning assistant. Extract ALL planning-relevant information from this Kanna Kickback 6 transcript.

AVAILABLE CATEGORIES:
{categories_list}

TRANSCRIPT CONTENT:
{transcript_content[:5000]}{'...' if len(transcript_content) > 5000 else ''}

EXTRACTION RULES:
1. Extract ANY information that could be useful for event planning
2. Assign each item to the most appropriate category name from the list above
3. Use specific, actionable titles
4. Include confidence levels (1-10) based on how clear/certain the information is
5. Add relevant tags for easier searching
6. Extract numbers, dates, names, locations, requirements, etc.
7. Even extract uncertain information - mark it with lower confidence

IMPORTANT: Return ONLY valid JSON in this exact format:

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

Focus on extracting:
- Attendance numbers and capacity planning
- Venue details and location information
- Food/catering plans and requirements
- Cannabis products and supply needs
- Partnership agreements and vendor relationships
- Budget/revenue information and financial planning
- Important dates and timeline information
- Staffing needs and volunteer requirements
- Equipment/supplies needed
- Legal/compliance considerations
- Marketing and promotional plans
- Risk factors and contingency planning

Extract everything relevant, even if uncertain - we can verify later."""

    async def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API for text generation."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "max_tokens": 4000
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
    def _parse_extraction_results(self, openrouter_response: str) -> List[ExtractedItem]:
        """Parse the JSON response from OpenRouter into ExtractedItem objects."""
        try:
            # Try to find JSON in the response
            json_start = openrouter_response.find('{')
            json_end = openrouter_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.error("No JSON found in OpenRouter response")
                logger.debug(f"Response: {openrouter_response}")
                return []
                
            json_str = openrouter_response[json_start:json_end]
            data = json.loads(json_str)
            
            items = []
            for item_data in data.get('extracted_items', []):
                try:
                    # Validate category exists
                    category_name = item_data.get('category_name', '').lower()
                    if category_name not in self.categories_map:
                        logger.warning(f"Unknown category: {category_name}")
                        continue
                        
                    item = ExtractedItem(**item_data)
                    items.append(item)
                except Exception as e:
                    logger.error(f"Failed to parse item: {e}")
                    continue
                    
            return items
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenRouter: {e}")
            logger.debug(f"Response: {openrouter_response}")
            return []
            
    async def extract_from_transcript(self, transcript_path: str) -> List[ExtractedItem]:
        """Extract planning items from a single transcript."""
        
        # Read transcript content
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
            
        logger.info(f"Processing transcript: {Path(transcript_path).name}")
        logger.info(f"Content length: {len(transcript_content)} characters")
            
        # Create extraction prompt
        prompt = self._create_extraction_prompt(transcript_content)
        
        # Call OpenRouter for extraction
        try:
            extracted_data = await self._call_openrouter(prompt)
            items = self._parse_extraction_results(extracted_data)
            logger.info(f"Extracted {len(items)} items from {Path(transcript_path).name}")
            return items
        except Exception as e:
            logger.error(f"Failed to extract from {transcript_path}: {e}")
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
            json.dumps({
                "extracted_at": datetime.now().isoformat(),
                "extraction_method": "manual_openrouter",
                "model": OPENROUTER_MODEL
            })
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
            'manual_openrouter',
            'manual_extractor',
            f"Manual extraction of {len(items)} items using {OPENROUTER_MODEL}",
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
                logger.info(f"  ✅ Saved: {item.title} (confidence: {item.confidence_level})")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to save item '{item.title}': {e}")
                continue
                
        logger.info(f"📊 Saved {saved_count}/{len(items)} items to database")
        return saved_count
        
    async def close(self):
        """Close database connections."""
        if self.db_pool:
            await self.db_pool.close()

async def interactive_extraction():
    """Interactive extraction process."""
    extractor = ManualExtractor()
    
    try:
        await extractor.initialize()
        
        # Check multiple possible locations for transcripts
        ingest_folder = Path("./ingest")
        gilbert_folder = Path("../kk6-transcript-synthesis/gilbert-transcripts")
        
        transcript_files = []
        
        # Check ingest folder first
        if ingest_folder.exists():
            transcript_files.extend(list(ingest_folder.glob("*.txt")))
        
        # Check gilbert transcripts folder
        if gilbert_folder.exists():
            transcript_files.extend(list(gilbert_folder.glob("*.txt")))
        
        # Remove duplicates and sort
        transcript_files = sorted(list(set(transcript_files)), key=lambda x: x.name)
        
        print(f"\n🎯 Manual KK6 Transcript Extraction")
        print(f"📁 Found {len(transcript_files)} transcript files")
        print(f"🤖 Using OpenRouter API with {OPENROUTER_MODEL}")
        print(f"💾 Database: KK6 Planning Database")
        
        if not transcript_files:
            print(f"\n📂 No transcript files found!")
            print(f"   • Place .txt files in: ./ingest/")
            print(f"   • Or use existing files in: ../kk6-transcript-synthesis/gilbert-transcripts/")
            
        print("-" * 60)
        
        while True:
            print(f"\n📋 Available transcripts:")
            for i, file in enumerate(transcript_files[:10], 1):
                print(f"  {i:2}. {file.name}")
            
            if len(transcript_files) > 10:
                print(f"     ... and {len(transcript_files) - 10} more")
            
            print(f"\n🔍 Options:")
            if transcript_files:
                print(f"  Enter number (1-{min(10, len(transcript_files))}) to process transcript")
            print(f"  'list' to see all files")
            print(f"  'refresh' to rescan for new files")
            print(f"  'copy' to copy specific files from gilbert-transcripts to ingest")
            print(f"  'status' to check database status")
            print(f"  'quit' to exit")
            
            choice = input(f"\n👉 Your choice: ").strip().lower()
            
            if choice == 'quit':
                break
            elif choice == 'list':
                print(f"\n📋 All transcript files:")
                for i, file in enumerate(transcript_files, 1):
                    print(f"  {i:3}. {file.name}")
                continue
            elif choice == 'status':
                # Show database status
                items_count = await extractor.db_pool.fetchval("SELECT COUNT(*) FROM planning_items")
                sources_count = await extractor.db_pool.fetchval("SELECT COUNT(*) FROM sources")
                print(f"\n📊 Database Status:")
                print(f"  Planning items: {items_count}")
                print(f"  Sources processed: {sources_count}")
                continue
            
            try:
                file_index = int(choice) - 1
                if 0 <= file_index < len(transcript_files):
                    transcript_file = transcript_files[file_index]
                    
                    print(f"\n🔄 Processing: {transcript_file.name}")
                    
                    items = await extractor.extract_from_transcript(str(transcript_file))
                    if items:
                        print(f"\n📋 Extracted {len(items)} items:")
                        for item in items:
                            print(f"  • {item.title} (confidence: {item.confidence_level})")
                        
                        save_choice = input(f"\n💾 Save these items to database? (y/n): ").strip().lower()
                        if save_choice == 'y':
                            saved_count = await extractor.save_to_database(items, transcript_file.name)
                            print(f"✅ Saved {saved_count} items to database")
                            print(f"🌐 View at: http://localhost:8090/web")
                        else:
                            print("❌ Items not saved")
                    else:
                        print("❌ No items extracted")
                else:
                    print("❌ Invalid file number")
            except ValueError:
                print("❌ Please enter a valid number")
        
        print(f"\n👋 Extraction session complete!")
        
    finally:
        await extractor.close()

if __name__ == "__main__":
    asyncio.run(interactive_extraction())