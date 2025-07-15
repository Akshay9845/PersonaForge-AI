#!/usr/bin/env python3
"""
Reddit Persona AI - Intelligent User Analysis Platform
Crafted by Akshay

A production-grade AI system that understands Reddit users through advanced NLP,
network analysis, and GPT-4 powered insights.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from dotenv import load_dotenv

from scraper import RedditScraper
from analyzer import PersonaAnalyzer
from persona_builder import PersonaBuilder
from visualizer import PersonaVisualizer
from web_dashboard import WebDashboard
from utils import setup_logging, create_output_dir, load_config

# Load environment variables
load_dotenv()

# Initialize Rich console for beautiful CLI
console = Console()

# ASCII Art Banner
BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██████╗ ███████╗██████╗ ██████╗ ██╗████████╗            ║
║    ██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝            ║
║    ██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║               ║
║    ██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║               ║
║    ██║  ██║███████╗██████╔╝██████╔╝██║   ██║               ║
║    ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝               ║
║                                                              ║
║    ██████╗ ███████╗██████╗ ███████╗ ██████╗ ███╗   ██╗     ║
║    ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔═══██╗████╗  ██║     ║
║    ██████╔╝█████╗  ██████╔╝█████╗  ██║   ██║██╔██╗ ██║     ║
║    ██╔══██╗██╔══╝  ██╔══██╗██╔══╝  ██║   ██║██║╚██╗██║     ║
║    ██║  ██║███████╗██║  ██║███████╗╚██████╔╝██║ ╚████║     ║
║    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝     ║
║                                                              ║
║    🚀 Intelligent User Analysis Platform                     ║
║    🤖 Powered by GPT-4 & Advanced NLP                        ║
║    👨‍💻 Crafted by Akshay                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""


def print_banner():
    """Display the beautiful ASCII art banner."""
    console.print(Panel(BANNER, style="bold blue"))


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', default='.env', help='Configuration file path')
def cli(debug: bool, config: str):
    """Reddit Persona AI - Intelligent User Analysis Platform"""
    if debug:
        os.environ['DEBUG'] = 'True'
    
    # Load configuration
    load_dotenv(config)
    setup_logging()
    
    # Print banner
    print_banner()


@cli.command()
@click.option('--username', required=True, help='Reddit username to analyze')
@click.option('--max-posts', default=None, help='Maximum number of posts to analyze (None for all available)')
@click.option('--max-comments', default=None, help='Maximum number of comments to analyze (None for all available)')
@click.option('--save-json', is_flag=True, help='Save persona as JSON')
@click.option('--generate-pdf', is_flag=True, help='Generate PDF report')
@click.option('--save-visualizations', is_flag=True, help='Save interactive visualizations')
@click.option('--output-dir', default='personas', help='Output directory')
def analyze(username: str, max_posts: Optional[int], max_comments: Optional[int], save_json: bool, 
            generate_pdf: bool, save_visualizations: bool, output_dir: str):
    """Analyze a Reddit user and generate a detailed persona."""
    
    console.print(f"\n[bold green]🎯 Analyzing Reddit User:[/bold green] [bold yellow]u/{username}[/bold yellow]")
    posts_display = "All available" if max_posts is None else str(max_posts)
    comments_display = "All available" if max_comments is None else str(max_comments)
    console.print(f"[dim]Posts: {posts_display} | Comments: {comments_display}[/dim]\n")
    
    # Create output directory
    create_output_dir(output_dir)
    
    async def run_analysis():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Step 1: Scrape Reddit data
                task1 = progress.add_task("🔍 Scraping Reddit data...", total=None)
                scraper = RedditScraper()
                user_data = await scraper.scrape_user(username, max_posts, max_comments)
                progress.update(task1, description="✅ Reddit data scraped successfully")
                
                if not user_data['posts'] and not user_data['comments']:
                    console.print("[bold red]❌ No data found for this user. They might be private or have no activity.[/bold red]")
                    return
                
                # Step 2: Analyze data
                task2 = progress.add_task("🧠 Analyzing user patterns...", total=None)
                analyzer = PersonaAnalyzer()
                analysis_results = await analyzer.analyze_user(user_data)
                progress.update(task2, description="✅ User patterns analyzed")
                
                # Step 3: Generate persona
                task3 = progress.add_task("🤖 Generating AI-powered persona...", total=None)
                builder = PersonaBuilder()
                persona = await builder.build_persona(user_data, analysis_results)
                progress.update(task3, description="✅ Persona generated")
                
                # Step 4: Create visualizations
                if save_visualizations:
                    task4 = progress.add_task("📊 Creating visualizations...", total=None)
                    visualizer = PersonaVisualizer()
                    viz_files = await visualizer.create_visualizations(persona, output_dir)
                    progress.update(task4, description="✅ Visualizations created")
                
                # Step 5: Save outputs
                task5 = progress.add_task("💾 Saving outputs...", total=None)
                
                # Save text persona
                persona_file = Path(output_dir) / f"{username}_persona.txt"
                with open(persona_file, 'w', encoding='utf-8') as f:
                    f.write(persona['formatted_text'])
                
                # Save JSON if requested
                if save_json:
                    import json
                    json_file = Path(output_dir) / f"{username}_persona.json"
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(persona, f, indent=2, ensure_ascii=False)
                
                # Generate PDF if requested
                if generate_pdf:
                    from utils import generate_pdf_report
                    pdf_file = await generate_pdf_report(persona, output_dir)
                
                progress.update(task5, description="✅ All outputs saved")
            
            # Display results
            console.print(f"\n[bold green]🎉 Analysis Complete![/bold green]")
            console.print(f"📄 Persona saved to: [bold blue]{persona_file}[/bold blue]")
            
            if save_json:
                console.print(f"📊 JSON data saved to: [bold blue]{json_file}[/bold blue]")
            if generate_pdf:
                console.print(f"📋 PDF report saved to: [bold blue]{pdf_file}[/bold blue]")
            if save_visualizations:
                console.print(f"📈 Visualizations saved to: [bold blue]{output_dir}/[/bold blue]")
            
            # Show persona summary
            console.print(f"\n[bold cyan]📋 Persona Summary:[/bold cyan]")
            
            # Handle different personality field structures
            personality_type = "Unknown"
            if 'personality_type' in persona:
                personality_type = persona['personality_type']
            elif 'personality' in persona and 'mbti_type' in persona['personality']:
                personality_type = persona['personality']['mbti_type']
            elif 'personality' in persona and 'type' in persona['personality']:
                personality_type = persona['personality']['type']
            
            confidence = persona.get('metadata', {}).get('confidence_overall', 0.0)
            console.print(f"🎭 Personality: {personality_type} ({confidence:.2f})")
            console.print(f"🎯 Top Interests: {', '.join(persona['interests'][:3])}")
            console.print(f"📝 Writing Style: {persona['writing_style']['summary']}")
            
        except Exception as e:
            console.print(f"[bold red]❌ Error during analysis: {str(e)}[/bold red]")
            if os.getenv('DEBUG'):
                import traceback
                console.print(traceback.format_exc())
    
    # Run the analysis
    asyncio.run(run_analysis())


@cli.command()
@click.option('--user1', required=True, help='First Reddit username')
@click.option('--user2', required=True, help='Second Reddit username')
@click.option('--output-dir', default='personas', help='Output directory')
def compare(user1: str, user2: str, output_dir: str):
    """Compare two Reddit users and find similarities/differences."""
    
    console.print(f"\n[bold green]🔄 Comparing Users:[/bold green]")
    console.print(f"[bold yellow]u/{user1}[/bold yellow] vs [bold yellow]u/{user2}[/bold yellow]\n")
    
    async def run_comparison():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Analyze both users
                scraper = RedditScraper()
                analyzer = PersonaAnalyzer()
                builder = PersonaBuilder()
                
                personas = {}
                for username in [user1, user2]:
                    task = progress.add_task(f"🔍 Analyzing u/{username}...", total=None)
                    
                    user_data = await scraper.scrape_user(username, None, None)
                    analysis_results = await analyzer.analyze_user(user_data)
                    persona = await builder.build_persona(user_data, analysis_results)
                    personas[username] = persona
                    
                    progress.update(task, description=f"✅ u/{username} analyzed")
                
                # Generate comparison
                task = progress.add_task("🔄 Generating comparison...", total=None)
                comparison = await builder.compare_personas(personas[user1], personas[user2])
                progress.update(task, description="✅ Comparison generated")
                
                # Save comparison
                comparison_file = Path(output_dir) / f"comparison_{user1}_vs_{user2}.txt"
                with open(comparison_file, 'w', encoding='utf-8') as f:
                    f.write(comparison['formatted_text'])
                
                # Display results
                console.print(f"\n[bold green]🎉 Comparison Complete![/bold green]")
                console.print(f"📄 Comparison saved to: [bold blue]{comparison_file}[/bold blue]")
                
                # Show key differences
                console.print(f"\n[bold cyan]🔍 Key Differences:[/bold cyan]")
                for diff in comparison['differences'][:5]:
                    console.print(f"• {diff}")
                
        except Exception as e:
            console.print(f"[bold red]❌ Error during comparison: {str(e)}[/bold red]")
    
    asyncio.run(run_comparison())


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8080, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def web(host: str, port: int, debug: bool):
    """Start the web dashboard."""
    
    console.print(f"\n[bold green]🌐 Starting Web Dashboard[/bold green]")
    console.print(f"📍 URL: [bold blue]http://{host}:{port}[/bold blue]")
    console.print(f"🔧 Debug: [bold yellow]{'Enabled' if debug else 'Disabled'}[/bold yellow]\n")
    
    dashboard = WebDashboard()
    dashboard.start(host=host, port=port, debug=debug)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--workers', default=4, help='Number of worker processes')
def api(host: str, port: int, workers: int):
    """Start the REST API server."""
    
    console.print(f"\n[bold green]🚀 Starting REST API Server[/bold green]")
    console.print(f"📍 URL: [bold blue]http://{host}:{port}[/bold blue]")
    console.print(f"📚 API Docs: [bold blue]http://{host}:{port}/docs[/bold blue]")
    console.print(f"👥 Workers: [bold yellow]{workers}[/bold yellow]\n")
    
    from web_dashboard import start_api_server
    start_api_server(host=host, port=port, workers=workers)


@cli.command()
def demo():
    """Run a demo analysis on a sample user."""
    
    console.print(f"\n[bold green]🎬 Running Demo Analysis[/bold green]")
    console.print(f"👤 Sample User: [bold yellow]u/kojied[/bold yellow]\n")
    
    # Run analysis with demo user
    analyze.callback(
        username='kojied',
        max_posts=20,
        max_comments=20,
        save_json=True,
        generate_pdf=True,
        save_visualizations=True,
        output_dir='personas'
    )


@cli.command()
def test():
    """Run the test suite."""
    
    console.print(f"\n[bold green]🧪 Running Test Suite[/bold green]\n")
    
    import subprocess
    import sys
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[bold green]✅ All tests passed![/bold green]")
        else:
            console.print("[bold red]❌ Some tests failed![/bold red]")
            console.print(result.stdout)
            console.print(result.stderr)
            
    except FileNotFoundError:
        console.print("[bold yellow]⚠️  pytest not found. Install with: pip install pytest[/bold yellow]")


if __name__ == '__main__':
    cli() 