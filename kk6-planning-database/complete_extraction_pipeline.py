#!/usr/bin/env python3
"""
Complete KK6 Extraction Pipeline
Demonstrates the full extraction workflow: embedding → extraction → deduplication → approval.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from iterative_extractor import IterativeExtractor
from deduplication_service import DeduplicationService
from approval_interface import ApprovalInterface, ApprovalAction

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KK6ExtractionPipeline:
    """Complete extraction pipeline for KK6 transcripts."""
    
    def __init__(self):
        self.extractor = None
        self.deduplication_service = None
        self.approval_interface = None
        
    async def initialize(self):
        """Initialize all pipeline components."""
        logger.info("🚀 Initializing KK6 Extraction Pipeline...")
        
        self.extractor = IterativeExtractor()
        await self.extractor.initialize()
        
        self.deduplication_service = DeduplicationService()
        await self.deduplication_service.initialize()
        
        self.approval_interface = ApprovalInterface()
        await self.approval_interface.initialize()
        
        logger.info("✅ Pipeline initialization complete")
        
    async def run_complete_pipeline(self, transcript_path: str, auto_approve: bool = False) -> Dict[str, Any]:
        """Run the complete extraction pipeline on a transcript."""
        
        logger.info(f"🎯 Starting complete extraction pipeline for: {Path(transcript_path).name}")
        
        # Step 1: Iterative Extraction
        logger.info("📊 Step 1: Running iterative category-by-category extraction...")
        extraction_result = await self.extractor.process_transcript_iteratively(transcript_path)
        session_id = extraction_result['session_id']
        
        logger.info(f"✅ Extraction complete: {extraction_result['total_items_extracted']} items from {extraction_result['categories_with_results']} categories")
        
        # Step 2: Deduplication Analysis
        logger.info("🔍 Step 2: Running deduplication analysis...")
        dedup_analysis = await self.deduplication_service.analyze_session_duplicates(session_id)
        
        duplicate_groups = len(dedup_analysis['duplicate_groups'])
        unique_items = dedup_analysis['summary']['unique_items']
        logger.info(f"✅ Deduplication complete: {unique_items} unique items, {duplicate_groups} duplicate groups")
        
        # Step 3: Display Results Summary
        self._display_pipeline_summary(extraction_result, dedup_analysis)
        
        # Step 4: Approval Process
        if auto_approve:
            logger.info("🤖 Step 3: Auto-approving all items for demo...")
            # Simulate approval of all items
            approved_count = await self._auto_approve_all_items(session_id)
            logger.info(f"✅ Auto-approved {approved_count} items")
            
            pipeline_result = {
                'transcript_file': Path(transcript_path).name,
                'session_id': session_id,
                'extraction_result': extraction_result,
                'deduplication_analysis': dedup_analysis,
                'approved_items': approved_count,
                'pipeline_status': 'completed'
            }
        else:
            logger.info("👤 Step 3: Interactive approval (run approval_interface.py separately)")
            pipeline_result = {
                'transcript_file': Path(transcript_path).name,
                'session_id': session_id,
                'extraction_result': extraction_result,
                'deduplication_analysis': dedup_analysis,
                'pipeline_status': 'ready_for_approval'
            }
        
        return pipeline_result
        
    def _display_pipeline_summary(self, extraction_result: Dict[str, Any], dedup_analysis: Dict[str, Any]):
        """Display a summary of the pipeline results."""
        print("\n" + "="*60)
        print("🎉 KK6 EXTRACTION PIPELINE SUMMARY")
        print("="*60)
        
        print(f"📁 Transcript: {extraction_result['transcript_file']}")
        print(f"📊 Session ID: {extraction_result['session_id']}")
        
        print(f"\n📋 EXTRACTION RESULTS:")
        print(f"  • Total categories processed: {extraction_result['categories_processed']}")
        print(f"  • Categories with results: {extraction_result['categories_with_results']}")
        print(f"  • Total items extracted: {extraction_result['total_items_extracted']}")
        print(f"  • Average confidence: {extraction_result['average_confidence']:.1f}/10")
        
        print(f"\n🔍 DEDUPLICATION ANALYSIS:")
        summary = dedup_analysis['summary']
        print(f"  • Total items analyzed: {summary['total_items']}")
        print(f"  • Duplicate groups found: {summary['duplicate_groups']}")
        print(f"  • Unique items: {summary['unique_items']}")
        print(f"  • Reduction percentage: {summary['reduction_percentage']:.1f}%")
        
        print(f"\n📋 ITEMS BY CATEGORY:")
        for category, items in dedup_analysis['items_by_category'].items():
            if items:
                print(f"  • {category.replace('_', ' ').title()}: {len(items)} items")
                for item in items[:2]:  # Show first 2 items
                    title = item.content.get('title', 'No title')
                    confidence = item.confidence_score * 10
                    print(f"    - {title[:50]}... (confidence: {confidence:.1f})")
                if len(items) > 2:
                    print(f"    ... and {len(items) - 2} more items")
        
        print("\n" + "="*60)
        
    async def _auto_approve_all_items(self, session_id: int) -> int:
        """Auto-approve all items for demonstration purposes."""
        
        # Get all items from the session
        items = await self.deduplication_service.get_extraction_results(session_id)
        
        approved_count = 0
        for item in items:
            try:
                content = item.content
                
                # Insert into planning_items table
                query = """
                    INSERT INTO planning_items (
                        category_id, title, description, status, priority_level,
                        estimated_cost, notes, tags, source_reference,
                        extracted_from, extraction_confidence
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """
                
                await self.approval_interface.db_pool.execute(
                    query,
                    item.category_id,
                    content.get('title', ''),
                    content.get('content', ''),
                    'pending',
                    content.get('priority_level', 3),
                    content.get('value_numeric'),
                    f"Auto-approved via pipeline demo (confidence: {item.confidence_score:.2f})",
                    content.get('tags', []),
                    f"extraction_session_{session_id}",
                    f"Session {session_id}, Result {item.result_id}",
                    item.confidence_score
                )
                
                approved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to auto-approve item {item.result_id}: {e}")
                continue
                
        return approved_count
        
    async def close(self):
        """Clean up all pipeline components."""
        if self.extractor:
            await self.extractor.close()
        if self.deduplication_service:
            await self.deduplication_service.close()
        if self.approval_interface:
            await self.approval_interface.close()

async def demo_complete_pipeline():
    """Demonstrate the complete extraction pipeline."""
    
    pipeline = KK6ExtractionPipeline()
    
    try:
        await pipeline.initialize()
        
        # Find transcript files
        ingest_folder = Path("./ingest")
        transcript_files = list(ingest_folder.glob("*.txt")) if ingest_folder.exists() else []
        
        if transcript_files:
            # Use the first transcript file for demo
            test_file = transcript_files[0]
            
            print(f"🎯 DEMO: Complete KK6 Extraction Pipeline")
            print(f"📁 Processing: {test_file.name}")
            print(f"🔄 Running: Embedding → Extraction → Deduplication → Auto-Approval")
            
            # Run complete pipeline with auto-approval
            result = await pipeline.run_complete_pipeline(str(test_file), auto_approve=True)
            
            print(f"\n✅ PIPELINE COMPLETE!")
            print(f"📊 Status: {result['pipeline_status']}")
            if 'approved_items' in result:
                print(f"💾 Approved and saved: {result['approved_items']} planning items")
            
            print(f"\n💡 Next steps:")
            print(f"  • Check planning_items table for saved results")
            print(f"  • Run approval_interface.py for interactive review")
            print(f"  • Process additional transcripts with this pipeline")
            
        else:
            print("❌ No transcript files found in ./ingest/")
            
    finally:
        await pipeline.close()

if __name__ == "__main__":
    asyncio.run(demo_complete_pipeline())