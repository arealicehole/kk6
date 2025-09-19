#!/usr/bin/env python3
"""Main script for processing transcripts from Gilbert folder."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .api import get_api_client
from .database import DatabaseManager, TranscriptRepository, TranscriptRecord
from .utils import get_settings

# Set up rich console
console = Console()

# Set up logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger(__name__)


class TranscriptProcessor:
    """Processes transcripts from Gilbert folder and stores analysis in database."""
    
    def __init__(self) -> None:
        """Initialize the processor."""
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
        self.repository = TranscriptRepository(self.db_manager)
        self.api_client = None
        
    async def initialize(self) -> None:
        """Initialize database and API client."""
        logger.info("Initializing transcript processor...")
        await self.db_manager.initialize()
        self.api_client = get_api_client()
        logger.info(f"Using API provider: {self.settings.api_provider}")
        
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.api_client:
            await self.api_client.close()
        await self.db_manager.close()
        
    def discover_transcript_files(self) -> List[Path]:
        """Discover all text files in the transcript folder.
        
        Returns:
            List of transcript file paths
            
        Raises:
            FileNotFoundError: If transcript folder doesn't exist
        """
        transcript_folder = self.settings.transcript_folder
        
        if not transcript_folder.exists():
            raise FileNotFoundError(f"Transcript folder not found: {transcript_folder}")
        
        if not transcript_folder.is_dir():
            raise ValueError(f"Transcript path is not a directory: {transcript_folder}")
        
        # Find all text files
        text_files = []
        for pattern in ["*.txt", "*.text"]:
            text_files.extend(transcript_folder.glob(pattern))
        
        # Sort by filename for consistent processing order
        text_files.sort()
        
        logger.info(f"Found {len(text_files)} transcript files in {transcript_folder}")
        return text_files
    
    async def process_transcript_file(self, file_path: Path) -> bool:
        """Process a single transcript file.
        
        Args:
            file_path: Path to transcript file
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Check if already processed
            existing = await self.repository.get_transcript_by_filename(file_path.name)
            if existing:
                logger.debug(f"Skipping already processed file: {file_path.name}")
                return True
            
            # Read file content
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Try with different encoding
                content = file_path.read_text(encoding="latin-1")
            
            if not content.strip():
                logger.warning(f"Empty file skipped: {file_path.name}")
                return False
            
            # Analyze with AI
            analysis = await self.api_client.analyze_transcript(content, file_path.name)
            
            # Create database record
            transcript = TranscriptRecord(
                filename=file_path.name,
                content=content,
                mentions_kickback=analysis.mentions_kickback,
                confidence_score=analysis.confidence_score,
                analysis_notes=analysis.analysis_notes,
                metadata={
                    "file_size": file_path.stat().st_size,
                    "relevant_quotes": analysis.relevant_quotes,
                    "file_path": str(file_path),
                }
            )
            
            # Save to database
            await self.repository.create_transcript(transcript)
            
            logger.info(
                f"Processed {file_path.name}: "
                f"mentions_kickback={analysis.mentions_kickback} "
                f"(confidence={analysis.confidence_score:.2f})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            return False
    
    async def process_all_transcripts(self) -> None:
        """Process all transcripts in the Gilbert folder."""
        # Discover files
        files = self.discover_transcript_files()
        
        if not files:
            console.print("[yellow]No transcript files found to process.[/yellow]")
            return
        
        # Process files with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task(
                "Processing transcripts...", 
                total=len(files)
            )
            
            successful = 0
            failed = 0
            
            for file_path in files:
                progress.update(task, description=f"Processing {file_path.name}")
                
                success = await self.process_transcript_file(file_path)
                if success:
                    successful += 1
                else:
                    failed += 1
                
                progress.advance(task)
        
        # Print summary
        console.print(f"\n[green]✅ Processing complete![/green]")
        console.print(f"   Successfully processed: {successful}")
        if failed > 0:
            console.print(f"   [red]Failed: {failed}[/red]")
        
        # Print analysis summary
        await self.print_analysis_summary()
    
    async def print_analysis_summary(self) -> None:
        """Print summary of analysis results."""
        total_count = await self.repository.count_transcripts()
        kickback_count = await self.repository.count_transcripts(mentions_kickback=True)
        no_kickback_count = await self.repository.count_transcripts(mentions_kickback=False)
        
        console.print(f"\n[bold]📊 Analysis Summary:[/bold]")
        console.print(f"   Total transcripts: {total_count}")
        console.print(f"   [green]✅ Mention Kanna Kickback: {kickback_count}[/green]")
        console.print(f"   [dim]❌ No mention: {no_kickback_count}[/dim]")
        
        if kickback_count > 0:
            # Show some examples
            console.print(f"\n[bold]🎯 Files mentioning Kanna Kickback:[/bold]")
            kickback_transcripts = await self.repository.list_transcripts(
                mentions_kickback=True, 
                limit=10
            )
            
            for transcript in kickback_transcripts:
                confidence_bar = "🟢" if transcript.confidence_score > 0.8 else "🟡"
                console.print(
                    f"   {confidence_bar} {transcript.filename} "
                    f"(confidence: {transcript.confidence_score:.2f})"
                )


async def main() -> None:
    """Main entry point."""
    console.print("[bold blue]🎤 KK6 Transcript Synthesis[/bold blue]")
    console.print("Processing transcripts from Gilbert folder...\n")
    
    processor = TranscriptProcessor()
    
    try:
        await processor.initialize()
        await processor.process_all_transcripts()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Processing interrupted by user.[/yellow]")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)
        
    finally:
        await processor.cleanup()
        console.print("\n[dim]Goodbye! 👋[/dim]")


if __name__ == "__main__":
    asyncio.run(main())