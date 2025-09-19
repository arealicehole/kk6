#!/usr/bin/env python3
"""
Parse conversation timestamps and metadata from transcript filenames.
Extract date, time, communication method, participants from structured filenames.
"""

import asyncio
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

class FilenameParser:
    """Parse temporal information from transcript filenames."""
    
    def __init__(self):
        self.db_pool = None
        
    async def initialize(self):
        """Initialize database connection."""
        self.db_pool = await asyncpg.create_pool(DATABASE_URL)
        
    def parse_filename(self, filename: str) -> Dict[str, Any]:
        """
        Parse filename to extract temporal metadata.
        
        Expected pattern: 
        '2025-08-07 11-54-37 (phone) Gilbert (+1 480-261-8175) ↙_transcription.txt'
        
        Returns dict with:
        - conversation_date: datetime
        - communication_method: str
        - participants: List[str]
        - phone_numbers: List[str]
        - raw_filename: str
        """
        
        # Remove file extension
        name_without_ext = Path(filename).stem
        
        # Pattern to match: YYYY-MM-DD HH-MM-SS (method) Name (+1 phone) extra
        pattern = r'^(\d{4}-\d{2}-\d{2})\s+(\d{2}-\d{2}-\d{2})\s+\((\w+)\)\s+([^(]+)(?:\s+\(([^)]+)\))?\s*(.*)$'
        
        match = re.match(pattern, name_without_ext)
        
        if not match:
            logger.warning(f"Could not parse filename: {filename}")
            return {
                'conversation_date': None,
                'communication_method': None,
                'participants': [],
                'phone_numbers': [],
                'raw_filename': filename,
                'parse_success': False
            }
            
        date_str, time_str, method, participant_info, phone_info, extra = match.groups()
        
        # Parse date and time
        try:
            # Convert time format from HH-MM-SS to HH:MM:SS
            time_formatted = time_str.replace('-', ':')
            datetime_str = f"{date_str} {time_formatted}"
            conversation_date = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            logger.error(f"Failed to parse datetime from {filename}: {e}")
            conversation_date = None
            
        # Extract participant name
        participant_name = participant_info.strip()
        participants = [participant_name] if participant_name else []
        
        # Extract phone numbers
        phone_numbers = []
        if phone_info:
            # Look for phone number patterns in the phone info
            phone_pattern = r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
            phone_matches = re.findall(phone_pattern, phone_info)
            for match in phone_matches:
                phone_numbers.append(f"+1 {match[0]}-{match[1]}-{match[2]}")
                
        return {
            'conversation_date': conversation_date,
            'communication_method': method.lower(),
            'participants': participants,
            'phone_numbers': phone_numbers,
            'raw_filename': filename,
            'parse_success': True,
            'extra_info': extra.strip() if extra else None
        }
        
    async def update_source_temporal_data(self, source_id: int, parsed_data: Dict[str, Any]) -> bool:
        """Update source record with parsed temporal data."""
        
        try:
            query = """
                UPDATE sources 
                SET 
                    conversation_date = $1,
                    communication_method = $2,
                    participants = $3,
                    conversation_sequence = $4
                WHERE id = $5
            """
            
            # Get sequence number by ordering by conversation_date
            if parsed_data['conversation_date']:
                seq_query = """
                    SELECT COUNT(*) + 1 as sequence
                    FROM sources 
                    WHERE conversation_date IS NOT NULL 
                    AND conversation_date < $1
                """
                seq_result = await self.db_pool.fetchrow(seq_query, parsed_data['conversation_date'])
                sequence = seq_result['sequence'] if seq_result else 1
            else:
                sequence = None
                
            await self.db_pool.execute(
                query,
                parsed_data['conversation_date'],
                parsed_data['communication_method'],
                parsed_data['participants'],
                sequence,
                source_id
            )
            
            logger.info(f"✅ Updated source {source_id} with temporal data")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update source {source_id}: {e}")
            return False
            
    async def process_all_sources(self) -> Dict[str, Any]:
        """Process all sources and update their temporal data."""
        
        # Get all sources
        sources = await self.db_pool.fetch("SELECT id, reference FROM sources ORDER BY id")
        
        results = {
            'total_sources': len(sources),
            'parsed_successfully': 0,
            'parse_failed': 0,
            'updated_successfully': 0,
            'update_failed': 0,
            'processed_sources': []
        }
        
        logger.info(f"🔄 Processing {len(sources)} sources...")
        
        for source in sources:
            source_id = source['id']
            filename = source['reference']
            
            logger.info(f"Processing source {source_id}: {filename}")
            
            # Parse filename
            parsed_data = self.parse_filename(filename)
            
            if parsed_data['parse_success']:
                results['parsed_successfully'] += 1
                
                # Update database
                if await self.update_source_temporal_data(source_id, parsed_data):
                    results['updated_successfully'] += 1
                else:
                    results['update_failed'] += 1
            else:
                results['parse_failed'] += 1
                
            results['processed_sources'].append({
                'source_id': source_id,
                'filename': filename,
                'parsed_data': parsed_data
            })
            
        return results
        
    async def display_parsed_results(self):
        """Display the parsed temporal data for verification."""
        
        query = """
            SELECT id, reference, conversation_date, communication_method, 
                   participants, conversation_sequence
            FROM sources 
            ORDER BY conversation_sequence NULLS LAST, conversation_date NULLS LAST, id
        """
        
        sources = await self.db_pool.fetch(query)
        
        print("\n📅 PARSED CONVERSATION TEMPORAL DATA:")
        print("=" * 80)
        
        for source in sources:
            print(f"\nSource {source['id']}: {source['reference']}")
            print(f"  📅 Date: {source['conversation_date']}")
            print(f"  🔢 Sequence: {source['conversation_sequence']}")
            print(f"  👥 Participants: {source['participants']}")
            print(f"  📞 Method: {source['communication_method']}")
            
    async def close(self):
        """Clean up resources."""
        if self.db_pool:
            await self.db_pool.close()

async def main():
    """Main function to parse and update conversation timestamps."""
    
    parser = FilenameParser()
    
    try:
        await parser.initialize()
        
        print("🔄 Parsing conversation timestamps from filenames...")
        
        # Process all sources
        results = await parser.process_all_sources()
        
        # Display summary
        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"Total sources: {results['total_sources']}")
        print(f"✅ Parsed successfully: {results['parsed_successfully']}")
        print(f"❌ Parse failed: {results['parse_failed']}")
        print(f"✅ Updated successfully: {results['updated_successfully']}")
        print(f"❌ Update failed: {results['update_failed']}")
        
        # Show parsed results
        await parser.display_parsed_results()
        
        # Show detailed parse results
        print(f"\n🔍 DETAILED PARSE RESULTS:")
        print("=" * 80)
        
        for processed in results['processed_sources']:
            data = processed['parsed_data']
            print(f"\nSource {processed['source_id']}: {processed['filename']}")
            print(f"  Parse success: {data['parse_success']}")
            if data['parse_success']:
                print(f"  Date: {data['conversation_date']}")
                print(f"  Method: {data['communication_method']}")
                print(f"  Participants: {data['participants']}")
                print(f"  Phone numbers: {data['phone_numbers']}")
                if data['extra_info']:
                    print(f"  Extra info: {data['extra_info']}")
        
    finally:
        await parser.close()

if __name__ == "__main__":
    asyncio.run(main())