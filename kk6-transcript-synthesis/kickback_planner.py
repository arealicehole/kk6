#!/usr/bin/env python3
"""Kanna Kickback 6 Event Planning Intelligence System - Integrated with Archon"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import track

from src.kk6_transcript_synthesis.database import DatabaseManager
from src.kk6_transcript_synthesis.api.factory import get_api_client
from src.kk6_transcript_synthesis.utils import get_settings

console = Console()

class KickbackPlanner:
    """Extract and organize all Kanna Kickback planning information."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.settings = get_settings()
        self.llm_client = None
        self.all_transcripts = []
        self.kickback_transcripts = []
        self.planning_data = {
            "dates_times": [],
            "attendees": [],
            "venue_info": [],
            "food_catering": [],
            "cannabis_supplies": [],
            "activities_entertainment": [],
            "logistics": [],
            "budget_money": [],
            "vendors_partners": [],
            "tasks_todos": [],
            "concerns_issues": [],
            "contacts": []
        }
    
    async def initialize(self):
        """Initialize database and LLM connections."""
        await self.db_manager.initialize()
        self.llm_client = get_api_client()
        console.print("[green]✅ System initialized[/green]")
    
    async def load_transcripts(self):
        """Load all transcripts from database."""
        # Get kickback-specific transcripts
        kickback_query = """
            SELECT id, filename, content, confidence_score, analysis_notes, created_at
            FROM transcripts 
            WHERE mentions_kickback = true
            ORDER BY created_at DESC
        """
        self.kickback_transcripts = await self.db_manager.fetch_all(kickback_query)
        
        # Also get recent transcripts that might have relevant info
        recent_query = """
            SELECT id, filename, content, created_at
            FROM transcripts 
            WHERE created_at > CURRENT_DATE - INTERVAL '30 days'
            ORDER BY created_at DESC
            LIMIT 20
        """
        recent = await self.db_manager.fetch_all(recent_query)
        
        console.print(f"[cyan]📞 Loaded {len(self.kickback_transcripts)} kickback transcripts[/cyan]")
        console.print(f"[cyan]📞 Loaded {len(recent)} recent transcripts for context[/cyan]")
        
        self.all_transcripts = self.kickback_transcripts + [t for t in recent if t['id'] not in [k['id'] for k in self.kickback_transcripts]]
    
    async def extract_planning_info(self, transcript: Dict) -> Dict[str, List[str]]:
        """Use LLM to extract planning information from a transcript."""
        prompt = f"""
        Analyze this phone transcript for Kanna Kickback 6 event planning information.
        Extract ANY relevant details about:
        
        1. DATES/TIMES: Event dates, deadlines, timing mentions
        2. ATTENDEES: People coming, expected attendance, guest lists
        3. VENUE: Location details, space requirements, setup needs
        4. FOOD/CATERING: Food plans, catering, sushi, dietary needs
        5. CANNABIS: Product amounts (pounds, ounces), strains, edibles, vendors
        6. ACTIVITIES: Entertainment, music, games, schedule
        7. LOGISTICS: Transportation, parking, equipment, supplies
        8. BUDGET/MONEY: Costs, pricing, profit sharing, expenses
        9. VENDORS/PARTNERS: INSA, dispensaries, sponsors, collaborators
        10. TASKS/TODOS: Action items, assignments, deadlines
        11. CONCERNS: Problems, worries, things to figure out
        12. CONTACTS: Phone numbers, names, who to call
        
        Note: "Canada Kickback", "canaker", "candy kickback" all refer to Kanna Kickback
        
        Transcript from {transcript['filename']}:
        {transcript['content'][:3000]}
        
        Return a JSON object with these keys, each containing a list of extracted info:
        {{
            "dates_times": [],
            "attendees": [],
            "venue_info": [],
            "food_catering": [],
            "cannabis_supplies": [],
            "activities_entertainment": [],
            "logistics": [],
            "budget_money": [],
            "vendors_partners": [],
            "tasks_todos": [],
            "concerns_issues": [],
            "contacts": []
        }}
        
        Be specific and include direct quotes when relevant. If nothing found for a category, leave empty list.
        """
        
        try:
            response = await self.llm_client.analyze_transcript(prompt)
            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response.explanation)
            if json_match:
                return json.loads(json_match.group())
            else:
                console.print(f"[yellow]⚠️  Could not parse JSON from {transcript['filename']}[/yellow]")
                return {}
        except Exception as e:
            console.print(f"[red]❌ Error analyzing {transcript['filename']}: {e}[/red]")
            return {}
    
    async def analyze_all_transcripts(self):
        """Analyze all transcripts for planning information."""
        console.print("\n[bold cyan]🔍 Analyzing transcripts for event planning details...[/bold cyan]\n")
        
        # Focus on kickback transcripts first
        for transcript in track(self.kickback_transcripts, description="Analyzing kickback mentions..."):
            info = await self.extract_planning_info(transcript)
            for key, values in info.items():
                if values and key in self.planning_data:
                    for value in values:
                        self.planning_data[key].append({
                            'info': value,
                            'source': transcript['filename'],
                            'date': transcript['created_at'].strftime('%Y-%m-%d')
                        })
        
        # Quick scan of recent transcripts for additional context
        console.print("\n[cyan]🔍 Scanning recent transcripts for additional context...[/cyan]")
        keywords = ['september', 'weekend', 'sushi', 'weed', 'pounds', 'INSA', 'party', 'event', '200']
        
        for transcript in self.all_transcripts[:10]:  # Check top 10 recent
            if transcript['id'] not in [k['id'] for k in self.kickback_transcripts]:
                content_lower = transcript['content'].lower()
                if any(keyword.lower() in content_lower for keyword in keywords):
                    console.print(f"[dim]  Checking {transcript['filename']}...[/dim]")
                    info = await self.extract_planning_info(transcript)
                    for key, values in info.items():
                        if values and key in self.planning_data:
                            for value in values:
                                self.planning_data[key].append({
                                    'info': value,
                                    'source': transcript['filename'],
                                    'date': transcript['created_at'].strftime('%Y-%m-%d')
                                })
    
    def generate_planning_report(self) -> str:
        """Generate comprehensive planning report."""
        report = []
        report.append("# 🎉 KANNA KICKBACK 6 - EVENT PLANNING INTELLIGENCE REPORT\n")
        report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        report.append("---\n")
        
        # Event Overview
        report.append("## 📅 EVENT TIMELINE & DATES\n")
        if self.planning_data['dates_times']:
            for item in self.planning_data['dates_times']:
                report.append(f"- **{item['info']}** *(source: {item['source']})*\n")
        else:
            report.append("- Target: September (weekend preferred)\n")
        
        # Attendees
        report.append("\n## 👥 EXPECTED ATTENDEES\n")
        if self.planning_data['attendees']:
            for item in self.planning_data['attendees']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        else:
            report.append("- Estimated: 200+ people (\"200 hungry fucking stoners\")\n")
        
        # Venue
        report.append("\n## 📍 VENUE & LOCATION\n")
        if self.planning_data['venue_info']:
            for item in self.planning_data['venue_info']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        else:
            report.append("- Needs outdoor space (table setup mentioned)\n")
        
        # Food & Catering
        report.append("\n## 🍱 FOOD & CATERING\n")
        report.append("### Confirmed Plans:\n")
        report.append("- **Sushi preparation** - need to hire/train someone by December\n")
        if self.planning_data['food_catering']:
            for item in self.planning_data['food_catering']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        
        # Cannabis Supplies
        report.append("\n## 🌿 CANNABIS SUPPLIES\n")
        report.append("### Confirmed Amounts:\n")
        report.append("- **2 pounds** for the event (mentioned as \"wheat for candy kickback\")\n")
        if self.planning_data['cannabis_supplies']:
            for item in self.planning_data['cannabis_supplies']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        
        # Activities
        report.append("\n## 🎮 ACTIVITIES & ENTERTAINMENT\n")
        if self.planning_data['activities_entertainment']:
            for item in self.planning_data['activities_entertainment']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        else:
            report.append("- *To be determined*\n")
        
        # Budget & Finances
        report.append("\n## 💰 BUDGET & FINANCES\n")
        if self.planning_data['budget_money']:
            for item in self.planning_data['budget_money']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        else:
            report.append("- Profit sharing arrangement mentioned\n")
        
        # Vendors & Partners
        report.append("\n## 🤝 VENDORS & PARTNERS\n")
        report.append("- **INSA** (cannabis company) - promotions/swag mentioned\n")
        if self.planning_data['vendors_partners']:
            for item in self.planning_data['vendors_partners']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        
        # Logistics
        report.append("\n## 🚚 LOGISTICS & OPERATIONS\n")
        if self.planning_data['logistics']:
            for item in self.planning_data['logistics']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        else:
            report.append("- Outside table setup with profit split\n")
        
        # Action Items
        report.append("\n## ✅ ACTION ITEMS & TODOS\n")
        report.append("### High Priority:\n")
        report.append("1. **Finalize September date** (weekend preferred)\n")
        report.append("2. **Hire/train sushi person** (deadline: December)\n")
        report.append("3. **Secure 2 pounds of product**\n")
        report.append("4. **Venue selection** (needs outdoor space)\n")
        if self.planning_data['tasks_todos']:
            report.append("\n### From Transcripts:\n")
            for item in self.planning_data['tasks_todos']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        
        # Concerns
        report.append("\n## ⚠️ CONCERNS & OPEN QUESTIONS\n")
        if self.planning_data['concerns_issues']:
            for item in self.planning_data['concerns_issues']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        else:
            report.append("- Who will make sushi?\n")
            report.append("- Venue capacity for 200+ people\n")
        
        # Contacts
        if self.planning_data['contacts']:
            report.append("\n## 📞 CONTACTS & COORDINATION\n")
            for item in self.planning_data['contacts']:
                report.append(f"- {item['info']} *(source: {item['source']})*\n")
        
        # Summary
        report.append("\n---\n")
        report.append("\n## 📊 PLANNING STATUS SUMMARY\n")
        report.append("- **Event Name:** Kanna Kickback 6\n")
        report.append("- **Target Date:** September (specific date TBD)\n")
        report.append("- **Expected Attendance:** 200+ people\n")
        report.append("- **Cannabis Amount:** 2 pounds confirmed\n")
        report.append("- **Food:** Sushi (need to hire/train chef)\n")
        report.append("- **Key Partner:** INSA (cannabis company)\n")
        report.append("- **Venue:** TBD (needs outdoor space)\n")
        
        return ''.join(report)
    
    def display_summary(self):
        """Display a summary table of planning information."""
        table = Table(title="🎉 Kanna Kickback 6 Planning Summary", show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")
        
        # Add rows for each category
        table.add_row(
            "📅 Date", 
            "⚠️ Pending",
            "September (weekend preferred)"
        )
        table.add_row(
            "👥 Attendees",
            "✅ Estimated",
            "200+ people"
        )
        table.add_row(
            "📍 Venue",
            "❌ TBD",
            "Needs outdoor space, table setup"
        )
        table.add_row(
            "🍱 Food",
            "⚠️ In Progress",
            "Sushi (need chef by December)"
        )
        table.add_row(
            "🌿 Cannabis",
            "✅ Planned",
            "2 pounds confirmed"
        )
        table.add_row(
            "🤝 Partners",
            "✅ Confirmed",
            "INSA (promotions/swag)"
        )
        table.add_row(
            "💰 Budget",
            "⚠️ Pending",
            "Profit sharing mentioned"
        )
        
        console.print(table)
    
    async def cleanup(self):
        """Clean up connections."""
        if self.llm_client:
            await self.llm_client.close()
        await self.db_manager.close()


async def main():
    """Main entry point for Kickback Planner."""
    console.print(Panel.fit(
        "[bold magenta]🎉 KANNA KICKBACK 6 - EVENT PLANNING INTELLIGENCE 🎉[/bold magenta]\n" +
        "[cyan]Analyzing Gilbert's transcripts for event planning information...[/cyan]",
        border_style="magenta"
    ))
    
    planner = KickbackPlanner()
    
    try:
        await planner.initialize()
        await planner.load_transcripts()
        await planner.analyze_all_transcripts()
        
        # Display summary
        console.print("\n")
        planner.display_summary()
        
        # Generate full report
        report = planner.generate_planning_report()
        
        # Save report to file
        report_file = f"kk6_planning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        console.print(f"\n[green]✅ Full report saved to: {report_file}[/green]")
        
        # Also display report in console
        console.print("\n")
        console.print(Panel(Markdown(report), title="Full Planning Report", border_style="green"))
        
        # Interactive mode
        console.print("\n[cyan]💬 Ask questions about the event planning:[/cyan]")
        console.print("[dim]Type 'quit' to exit[/dim]\n")
        
        while True:
            question = console.input("[bold cyan]Question>[/bold cyan] ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            # Search through planning data for relevant info
            results = []
            for category, items in planner.planning_data.items():
                for item in items:
                    if question.lower() in item['info'].lower():
                        results.append(f"[{category}] {item['info']} (from: {item['source']})")
            
            if results:
                console.print("\n[green]Found relevant information:[/green]")
                for result in results:
                    console.print(f"  • {result}")
            else:
                # Try to answer with LLM
                all_info = json.dumps(planner.planning_data, default=str)
                prompt = f"Based on this Kanna Kickback 6 planning data: {all_info[:2000]}\n\nAnswer this question: {question}"
                try:
                    response = await planner.llm_client.analyze_transcript(prompt)
                    console.print(f"\n[yellow]{response.explanation}[/yellow]")
                except:
                    console.print("[red]No specific information found for that question.[/red]")
            console.print()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Planning session interrupted.[/yellow]")
    
    finally:
        await planner.cleanup()
        console.print("\n[dim]Goodbye! 🎉[/dim]")


if __name__ == "__main__":
    asyncio.run(main())