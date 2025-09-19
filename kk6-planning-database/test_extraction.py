#!/usr/bin/env python3
"""
Test the extraction process on the 5 specific Kanna Kickback transcripts.
"""

import asyncio
from kk6_transcript_extractor import TranscriptExtractor

# The 5 specific transcripts that mention Kanna Kickback
TARGET_TRANSCRIPTS = [
    "2025-07-29 09-43-47 (phone) Gilbert (+1 480-261-8175) ↙_transcription.txt",
    "2025-08-07 11-54-37 (phone) Gilbert (+1 480-261-8175) ↙_transcription.txt", 
    "2025-08-20 09-34-19 (phone) Gilbert (+1 480-261-8175) ↙_transcription.txt",
    "2025-08-26 09-57-00 (phone) Gilbert (+1 480-261-8175) ↗_transcription.txt",
    "2025-09-12 10-47-14 (phone) Gilbert (+1 480-261-8175) ↙_transcription.txt"
]

async def test_specific_transcripts():
    """Test extraction on the 5 specific Kanna Kickback transcripts."""
    extractor = TranscriptExtractor()
    
    try:
        await extractor.initialize()
        
        total_items = 0
        for transcript_file in TARGET_TRANSCRIPTS:
            transcript_path = f"../kk6-transcript-synthesis/gilbert-transcripts/{transcript_file}"
            print(f"\nProcessing: {transcript_file}")
            
            try:
                items = await extractor.extract_from_transcript(transcript_path)
                if items:
                    saved_count = await extractor.save_to_database(items, transcript_file)
                    print(f"  Extracted: {len(items)} items")
                    print(f"  Saved: {saved_count} items")
                    total_items += saved_count
                    
                    # Show sample items
                    print("  Sample items:")
                    for item in items[:3]:  # Show first 3 items
                        print(f"    - {item.title} (confidence: {item.confidence_level})")
                else:
                    print("  No items extracted")
                    
            except Exception as e:
                print(f"  Error: {e}")
                
        print(f"\n=== TOTAL ITEMS EXTRACTED: {total_items} ===")
        print("View results at: http://localhost:8090/web")
        
    finally:
        await extractor.close()

if __name__ == "__main__":
    asyncio.run(test_specific_transcripts())