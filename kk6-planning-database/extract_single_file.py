#!/usr/bin/env python3
"""
Extract from a single specific transcript file.
Usage: python extract_single_file.py "filename.txt"
"""

import asyncio
import sys
from pathlib import Path
from iterative_extractor import IterativeExtractor

async def extract_single_file(filename: str):
    """Extract from a specific transcript file."""
    
    # Find the file
    ingest_folder = Path("./ingest")
    file_path = ingest_folder / filename
    
    if not file_path.exists():
        print(f"❌ File not found: {filename}")
        print(f"Available files:")
        for f in ingest_folder.glob("*.txt"):
            print(f"  - {f.name}")
        return
    
    # Run extraction
    extractor = IterativeExtractor()
    
    try:
        await extractor.initialize()
        
        print(f"🎯 Processing: {filename}")
        result = await extractor.process_transcript_iteratively(str(file_path))
        
        print(f"\n🎯 EXTRACTION RESULTS:")
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
                    
    finally:
        await extractor.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_single_file.py 'filename.txt'")
        print("\nAvailable files:")
        ingest_folder = Path("./ingest")
        for f in ingest_folder.glob("*.txt"):
            print(f"  - {f.name}")
    else:
        filename = sys.argv[1]
        asyncio.run(extract_single_file(filename))