#!/usr/bin/env python3
"""Script to add vector embeddings to existing transcript records."""

import asyncio
import logging
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

from src.kk6_transcript_synthesis.api.embeddings import OllamaEmbeddingClient
from src.kk6_transcript_synthesis.database import DatabaseManager, TranscriptRepository, TranscriptRecord
from src.kk6_transcript_synthesis.utils import get_settings

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


class EmbeddingProcessor:
    """Processes existing transcripts to add vector embeddings."""
    
    def __init__(self) -> None:
        """Initialize the embedding processor."""
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
        self.repository = TranscriptRepository(self.db_manager)
        self.embedding_client = None
        
    async def initialize(self) -> None:
        """Initialize database and embedding client."""
        logger.info("Initializing embedding processor...")
        await self.db_manager.initialize()
        
        # Create Ollama embedding client
        self.embedding_client = OllamaEmbeddingClient(
            host=self.settings.ollama_host,
            model="nomic-embed-text"  # Use nomic model which supports embeddings API
        )
        logger.info(f"Using Ollama embedding model: nomic-embed-text")
        
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.embedding_client:
            await self.embedding_client.close()
        await self.db_manager.close()
    
    async def get_transcripts_without_embeddings(self) -> List[TranscriptRecord]:
        """Get all transcript records that don't have embeddings yet.
        
        Returns:
            List of transcript records missing embeddings
        """
        # Get all transcripts (we'll filter in Python since SQL is simpler)
        all_transcripts = await self.repository.list_transcripts(limit=None)
        
        # Filter to only those without embeddings
        missing_embeddings = [
            transcript for transcript in all_transcripts 
            if transcript.embedding is None or len(transcript.embedding) == 0
        ]
        
        logger.info(f"Found {len(missing_embeddings)} transcripts without embeddings")
        return missing_embeddings
    
    async def process_transcript_embedding(self, transcript: TranscriptRecord) -> bool:
        """Generate and save embedding for a single transcript.
        
        Args:
            transcript: Transcript record to process
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding for the transcript content
            embedding = await self.embedding_client.generate_embedding(transcript.content)
            
            if not embedding:
                logger.warning(f"Empty embedding generated for {transcript.filename}")
                return False
            
            # Update the transcript with the embedding
            transcript.embedding = embedding
            await self.repository.update_transcript(transcript)
            
            logger.debug(f"Added embedding to {transcript.filename} ({len(embedding)} dimensions)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for {transcript.filename}: {e}")
            return False
    
    async def process_all_embeddings(self) -> None:
        """Process all transcripts to add embeddings."""
        # Get transcripts without embeddings
        transcripts = await self.get_transcripts_without_embeddings()
        
        if not transcripts:
            console.print("[green]✅ All transcripts already have embeddings![/green]")
            return
        
        console.print(f"[yellow]🔄 Processing {len(transcripts)} transcripts to add embeddings...[/yellow]")
        
        # Process transcripts with progress bar
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
                "Generating embeddings...", 
                total=len(transcripts)
            )
            
            successful = 0
            failed = 0
            
            for transcript in transcripts:
                progress.update(task, description=f"Embedding {transcript.filename}")
                
                success = await self.process_transcript_embedding(transcript)
                if success:
                    successful += 1
                else:
                    failed += 1
                
                progress.advance(task)
        
        # Print summary
        console.print(f"\n[green]✅ Embedding generation complete![/green]")
        console.print(f"   Successfully embedded: {successful}")
        if failed > 0:
            console.print(f"   [red]Failed: {failed}[/red]")
        
        # Print final status
        await self.print_embedding_summary()
    
    async def print_embedding_summary(self) -> None:
        """Print summary of embedding status."""
        total_count = await self.repository.count_transcripts()
        
        # Count records with embeddings by checking the database directly
        query = "SELECT COUNT(*) as count FROM transcripts WHERE embedding IS NOT NULL"
        result = await self.db_manager.fetch_one(query)
        embedded_count = result["count"] if result else 0
        
        console.print(f"\n[bold]📊 Embedding Summary:[/bold]")
        console.print(f"   Total transcripts: {total_count}")
        console.print(f"   [green]✅ With embeddings: {embedded_count}[/green]")
        console.print(f"   [dim]❌ Without embeddings: {total_count - embedded_count}[/dim]")
        
        if embedded_count > 0:
            console.print(f"\n[bold]🔍 Vector similarity search is now enabled![/bold]")


async def main() -> None:
    """Main entry point."""
    console.print("[bold blue]🧮 KK6 Transcript Embedding Generator[/bold blue]")
    console.print("Adding vector embeddings to existing transcript records...\n")
    
    processor = EmbeddingProcessor()
    
    try:
        await processor.initialize()
        await processor.process_all_embeddings()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Embedding generation interrupted by user.[/yellow]")
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        
    finally:
        await processor.cleanup()
        console.print("\n[dim]Done! 👋[/dim]")


if __name__ == "__main__":
    asyncio.run(main())