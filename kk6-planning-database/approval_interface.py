#!/usr/bin/env python3
"""
KK6 Interactive Approval Interface
Allows users to review, approve, edit, or decline extracted planning items.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import asyncpg
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import print as rprint

from deduplication_service import DeduplicationService, ExtractedItem, DuplicateGroup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/kk6_planning"

class ApprovalAction(Enum):
    APPROVE = "approve"
    EDIT = "edit" 
    DECLINE = "decline"
    SKIP = "skip"

@dataclass
class ApprovalDecision:
    """Represents a user's decision on an extracted item."""
    item: ExtractedItem
    action: ApprovalAction
    edited_content: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class ApprovalInterface:
    """Interactive interface for reviewing and approving extracted items."""
    
    def __init__(self):
        self.console = Console()
        self.db_pool = None
        self.deduplication_service = None
        
    async def initialize(self):
        """Initialize database connection and services."""
        self.db_pool = await asyncpg.create_pool(DATABASE_URL)
        self.deduplication_service = DeduplicationService()
        await self.deduplication_service.initialize()
        
    def display_welcome(self):
        """Display welcome message and instructions."""
        self.console.clear()
        welcome_panel = Panel.fit(
            "[bold blue]🎉 KK6 Extraction Results Approval Interface[/bold blue]\n\n"
            "Review extracted planning items from your KK6 transcripts.\n"
            "For each item you can:\n"
            "• [green]Approve[/green] - Accept the item as-is\n"
            "• [yellow]Edit[/yellow] - Modify the content before approval\n"
            "• [red]Decline[/red] - Reject the item\n"
            "• [blue]Skip[/blue] - Come back to this item later\n\n"
            "Approved items will be saved to your planning database.",
            title="Welcome"
        )
        self.console.print(welcome_panel)
        
    def display_extraction_summary(self, analysis: Dict[str, Any]):
        """Display summary of extraction results."""
        summary = analysis['summary']
        
        summary_table = Table(title="📊 Extraction Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")
        
        summary_table.add_row("Total Items", str(summary['total_items']))
        summary_table.add_row("Categories with Results", str(len(analysis['items_by_category'])))
        summary_table.add_row("Duplicate Groups", str(summary['duplicate_groups']))
        summary_table.add_row("Unique Items", str(summary['unique_items']))
        
        self.console.print(summary_table)
        self.console.print()
        
    def display_items_by_category(self, items_by_category: Dict[str, List[ExtractedItem]]):
        """Display extracted items organized by category."""
        for category_name, items in items_by_category.items():
            if not items:
                continue
                
            category_table = Table(title=f"📋 {category_name.replace('_', ' ').title()} ({len(items)} items)")
            category_table.add_column("Title", style="cyan", width=40)
            category_table.add_column("Content", style="white", width=50)
            category_table.add_column("Conf.", style="green", width=6)
            category_table.add_column("Tags", style="yellow", width=20)
            
            for item in items:
                content = item.content
                title = content.get('title', 'No title')[:37] + "..." if len(content.get('title', '')) > 40 else content.get('title', 'No title')
                item_content = content.get('content', 'No content')[:47] + "..." if len(content.get('content', '')) > 50 else content.get('content', 'No content')
                confidence = f"{item.confidence_score * 10:.1f}/10"
                tags = ", ".join(content.get('tags', [])[:3])  # Show first 3 tags
                
                category_table.add_row(title, item_content, confidence, tags)
                
            self.console.print(category_table)
            self.console.print()
            
    def display_duplicate_groups(self, duplicate_groups: List[DuplicateGroup]):
        """Display duplicate groups if any exist."""
        if not duplicate_groups:
            return
            
        self.console.print("[bold red]🔄 Duplicate Groups Found[/bold red]\n")
        
        for i, group in enumerate(duplicate_groups, 1):
            dup_table = Table(title=f"Duplicate Group {i}")
            dup_table.add_column("Type", style="cyan")
            dup_table.add_column("Category", style="yellow")  
            dup_table.add_column("Title", style="white")
            dup_table.add_column("Similarity", style="green")
            
            # Primary item
            primary = group.primary_item
            dup_table.add_row(
                "PRIMARY",
                primary.category_name,
                primary.content.get('title', 'No title')[:30],
                "100%"
            )
            
            # Duplicate items
            for j, (duplicate, similarity) in enumerate(zip(group.duplicates, group.similarity_scores)):
                dup_table.add_row(
                    f"DUP #{j+1}",
                    duplicate.category_name,
                    duplicate.content.get('title', 'No title')[:30],
                    f"{similarity*100:.1f}%"
                )
                
            self.console.print(dup_table)
            
            # Show merge suggestion
            merge = group.merge_suggestion
            merge_panel = Panel(
                f"[bold]Suggested Merge:[/bold]\n"
                f"Title: {merge.get('title', 'N/A')}\n"
                f"Categories: {', '.join(merge.get('source_categories', []))}\n"
                f"Content: {merge.get('content', 'N/A')[:100]}...",
                title="🔧 Merge Suggestion"
            )
            self.console.print(merge_panel)
            self.console.print()
            
    async def review_item(self, item: ExtractedItem) -> ApprovalDecision:
        """Interactive review of a single item."""
        content = item.content
        
        # Create item display panel
        item_text = (
            f"[bold cyan]Category:[/bold cyan] {item.category_name}\n"
            f"[bold green]Title:[/bold green] {content.get('title', 'No title')}\n"
            f"[bold white]Content:[/bold white] {content.get('content', 'No content')}\n"
            f"[bold yellow]Confidence:[/bold yellow] {item.confidence_score * 10:.1f}/10\n"
            f"[bold magenta]Tags:[/bold magenta] {', '.join(content.get('tags', []))}"
        )
        
        item_panel = Panel(item_text, title="📋 Review Item", width=80)
        self.console.print(item_panel)
        
        # Get user choice
        while True:
            choice = Prompt.ask(
                "\nWhat would you like to do?",
                choices=["approve", "edit", "decline", "skip"],
                default="approve"
            )
            
            if choice == "approve":
                return ApprovalDecision(item, ApprovalAction.APPROVE)
                
            elif choice == "edit":
                edited_content = await self._edit_item_content(content)
                if edited_content:
                    return ApprovalDecision(item, ApprovalAction.EDIT, edited_content)
                # If user cancels edit, continue loop
                
            elif choice == "decline":
                notes = Prompt.ask("Reason for declining (optional)", default="")
                return ApprovalDecision(item, ApprovalAction.DECLINE, notes=notes)
                
            elif choice == "skip":
                return ApprovalDecision(item, ApprovalAction.SKIP)
                
    async def _edit_item_content(self, original_content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Allow user to edit item content."""
        self.console.print("\n[bold blue]📝 Edit Item Content[/bold blue]")
        self.console.print("Press Enter to keep current value, or type new value:")
        
        edited_content = original_content.copy()
        
        # Edit title
        current_title = original_content.get('title', '')
        new_title = Prompt.ask(f"Title [{current_title}]", default=current_title)
        if new_title != current_title:
            edited_content['title'] = new_title
            
        # Edit content
        current_content = original_content.get('content', '')
        new_content = Prompt.ask(f"Content [{current_content[:50]}...]", default=current_content)
        if new_content != current_content:
            edited_content['content'] = new_content
            
        # Edit confidence level
        current_confidence = original_content.get('confidence_level', 5)
        new_confidence = Prompt.ask(
            f"Confidence (1-10) [{current_confidence}]",
            default=str(current_confidence)
        )
        try:
            edited_content['confidence_level'] = int(new_confidence)
        except ValueError:
            edited_content['confidence_level'] = current_confidence
            
        # Edit tags
        current_tags = ', '.join(original_content.get('tags', []))
        new_tags = Prompt.ask(f"Tags (comma-separated) [{current_tags}]", default=current_tags)
        if new_tags != current_tags:
            edited_content['tags'] = [tag.strip() for tag in new_tags.split(',') if tag.strip()]
            
        # Confirm changes
        if Confirm.ask("Save these changes?"):
            return edited_content
        return None
        
    async def save_approved_items(self, approved_items: List[ApprovalDecision]) -> int:
        """Save approved items to the planning database."""
        saved_count = 0
        
        for decision in approved_items:
            if decision.action not in [ApprovalAction.APPROVE, ApprovalAction.EDIT]:
                continue
                
            try:
                content = decision.edited_content if decision.action == ApprovalAction.EDIT else decision.item.content
                
                # Insert into planning_items table
                query = """
                    INSERT INTO planning_items (
                        category_id, title, description, status, priority_level,
                        assigned_to, estimated_cost, notes, tags, source_reference,
                        extracted_from, extraction_confidence
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """
                
                await self.db_pool.execute(
                    query,
                    decision.item.category_id,
                    content.get('title', ''),
                    content.get('content', ''),
                    'pending',  # Default status
                    content.get('priority_level', 3),
                    None,  # assigned_to
                    content.get('value_numeric'),  # estimated_cost
                    decision.notes or f"Extracted via iterative extraction (confidence: {decision.item.confidence_score:.2f})",
                    content.get('tags', []),
                    f"extraction_session_{decision.item.session_id}",
                    f"Session {decision.item.session_id}, Result {decision.item.result_id}",
                    decision.item.confidence_score
                )
                
                saved_count += 1
                logger.info(f"Saved approved item: {content.get('title', 'Untitled')}")
                
            except Exception as e:
                logger.error(f"Failed to save item {decision.item.result_id}: {e}")
                continue
                
        logger.info(f"Successfully saved {saved_count} approved items to planning database")
        return saved_count
        
    async def run_approval_session(self, session_id: int) -> Dict[str, Any]:
        """Run complete approval session for an extraction session."""
        
        self.display_welcome()
        
        # Get deduplication analysis
        self.console.print("🔍 Analyzing extraction results...\n")
        analysis = await self.deduplication_service.analyze_session_duplicates(session_id)
        
        if analysis['summary']['total_items'] == 0:
            self.console.print("[red]❌ No extraction results found for this session.[/red]")
            return analysis
            
        # Display summary
        self.display_extraction_summary(analysis)
        
        # Show items by category
        self.console.print("[bold]📋 Extracted Items by Category:[/bold]\n")
        self.display_items_by_category(analysis['items_by_category'])
        
        # Show duplicates if any
        self.display_duplicate_groups(analysis['duplicate_groups'])
        
        # Ask if user wants to proceed with review
        if not Confirm.ask("\nProceed with item-by-item review?"):
            return analysis
            
        # Review each item
        decisions = []
        all_items = []
        
        # Collect all items (unique items + primary items from duplicate groups)
        for items in analysis['items_by_category'].values():
            all_items.extend(items)
            
        self.console.print(f"\n[bold blue]Starting review of {len(all_items)} items...[/bold blue]\n")
        
        for i, item in enumerate(all_items, 1):
            self.console.print(f"\n[bold]Item {i} of {len(all_items)}[/bold]")
            decision = await self.review_item(item)
            decisions.append(decision)
            
            if decision.action == ApprovalAction.SKIP:
                self.console.print("[yellow]⏭️  Skipped - you can review this later[/yellow]")
            elif decision.action == ApprovalAction.APPROVE:
                self.console.print("[green]✅ Approved[/green]")
            elif decision.action == ApprovalAction.EDIT:
                self.console.print("[yellow]📝 Approved with edits[/yellow]")
            elif decision.action == ApprovalAction.DECLINE:
                self.console.print("[red]❌ Declined[/red]")
                
        # Summary of decisions
        approved_count = sum(1 for d in decisions if d.action in [ApprovalAction.APPROVE, ApprovalAction.EDIT])
        declined_count = sum(1 for d in decisions if d.action == ApprovalAction.DECLINE)
        skipped_count = sum(1 for d in decisions if d.action == ApprovalAction.SKIP)
        
        summary_panel = Panel(
            f"[green]✅ Approved: {approved_count}[/green]\n"
            f"[red]❌ Declined: {declined_count}[/red]\n"
            f"[yellow]⏭️  Skipped: {skipped_count}[/yellow]",
            title="📊 Review Summary"
        )
        self.console.print(summary_panel)
        
        # Save approved items
        if approved_count > 0 and Confirm.ask(f"\nSave {approved_count} approved items to planning database?"):
            saved_count = await self.save_approved_items(decisions)
            self.console.print(f"[green]✅ Successfully saved {saved_count} items to planning database![/green]")
        
        return {
            **analysis,
            'approval_decisions': decisions,
            'approved_count': approved_count,
            'declined_count': declined_count,
            'skipped_count': skipped_count
        }
        
    async def close(self):
        """Clean up resources."""
        if self.deduplication_service:
            await self.deduplication_service.close()
        if self.db_pool:
            await self.db_pool.close()

async def main():
    """Main entry point for approval interface."""
    interface = ApprovalInterface()
    
    try:
        await interface.initialize()
        
        # Get latest extraction session
        latest_session = await interface.db_pool.fetchrow(
            "SELECT id FROM extraction_sessions ORDER BY completed_at DESC LIMIT 1"
        )
        
        if latest_session:
            session_id = latest_session['id']
            result = await interface.run_approval_session(session_id)
            print(f"\n🎉 Approval session complete for session {session_id}")
        else:
            print("❌ No extraction sessions found")
            
    finally:
        await interface.close()

if __name__ == "__main__":
    asyncio.run(main())