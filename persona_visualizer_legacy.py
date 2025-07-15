"""
Persona Visualizer Module
Creates interactive charts and visualizations for enhanced personas.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

logger = logging.getLogger(__name__)

class PersonaVisualizer:
    """Creates interactive visualizations for enhanced personas."""
    
    def __init__(self):
        """Initialize the persona visualizer."""
        self.output_dir = Path("personas")
        self.output_dir.mkdir(exist_ok=True)
    
    def create_personality_radar(self, persona_data: Dict[str, Any], output_path: str = None) -> str:
        """Create a radar chart for personality dimensions."""
        
        personality = persona_data.get('personality', {})
        if not personality:
            return None
        
        # Prepare data for radar chart
        categories = list(personality.keys())
        values = list(personality.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Personality Profile',
            line_color='rgb(102, 126, 234)',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title=f"Personality Profile - {persona_data.get('name', 'User')}",
            font=dict(size=12)
        )
        
        if output_path:
            fig.write_html(output_path)
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_motivations_bar(self, persona_data: Dict[str, Any], output_path: str = None) -> str:
        """Create a bar chart for motivations."""
        
        motivations = persona_data.get('motivations', {})
        if not motivations:
            return None
        
        # Prepare data
        categories = list(motivations.keys())
        values = list(motivations.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color='rgb(118, 75, 162)',
                text=values,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"Motivations - {persona_data.get('name', 'User')}",
            xaxis_title="Motivation Factors",
            yaxis_title="Score (0-100)",
            yaxis=dict(range=[0, 100]),
            font=dict(size=12)
        )
        
        if output_path:
            fig.write_html(output_path)
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_traits_cloud(self, persona_data: Dict[str, Any], output_path: str = None) -> str:
        """Create a word cloud for personality traits."""
        
        traits = persona_data.get('traits', [])
        if not traits:
            return None
        
        # Create a simple bar chart as word cloud alternative
        fig = go.Figure(data=[
            go.Bar(
                x=traits,
                y=[len(trait) * 10 for trait in traits],  # Size based on word length
                marker_color='rgb(102, 126, 234)',
                text=traits,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f"Personality Traits - {persona_data.get('name', 'User')}",
            xaxis_title="Traits",
            yaxis_title="Relative Size",
            font=dict(size=12)
        )
        
        if output_path:
            fig.write_html(output_path)
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_activity_timeline(self, persona_data: Dict[str, Any], output_path: str = None) -> str:
        """Create an activity timeline chart."""
        
        data_sources = persona_data.get('data_sources', [])
        if not data_sources:
            return None
        
        # Create timeline data
        timeline_data = []
        for i, source in enumerate(data_sources[:10]):  # Limit to 10 sources
            timeline_data.append({
                'Time': f"Activity {i+1}",
                'Type': source.get('type', 'Unknown'),
                'Subreddit': source.get('subreddit', 'Unknown'),
                'Text': source.get('text', '')[:50] + "..."
            })
        
        df = pd.DataFrame(timeline_data)
        
        fig = px.timeline(df, x_start='Time', y='Type', 
                         color='Subreddit', text='Text',
                         title=f"Activity Timeline - {persona_data.get('name', 'User')}")
        
        fig.update_layout(
            font=dict(size=10),
            height=400
        )
        
        if output_path:
            fig.write_html(output_path)
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_comprehensive_dashboard(self, persona_data: Dict[str, Any], output_path: str = None) -> str:
        """Create a comprehensive dashboard with multiple charts."""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Personality Profile', 'Motivations', 'Traits', 'Activity'),
            specs=[[{"type": "polar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Personality radar
        personality = persona_data.get('personality', {})
        if personality:
            categories = list(personality.keys())
            values = list(personality.values())
            
            fig.add_trace(
                go.Scatterpolar(r=values, theta=categories, fill='toself', name='Personality'),
                row=1, col=1
            )
        
        # Motivations bar
        motivations = persona_data.get('motivations', {})
        if motivations:
            categories = list(motivations.keys())
            values = list(motivations.values())
            
            fig.add_trace(
                go.Bar(x=categories, y=values, name='Motivations'),
                row=1, col=2
            )
        
        # Traits bar
        traits = persona_data.get('traits', [])
        if traits:
            fig.add_trace(
                go.Bar(x=traits, y=[len(trait) * 10 for trait in traits], name='Traits'),
                row=2, col=1
            )
        
        # Activity scatter (simplified)
        data_sources = persona_data.get('data_sources', [])
        if data_sources:
            x_vals = list(range(len(data_sources[:10])))
            y_vals = [i * 10 for i in range(len(data_sources[:10]))]
            
            fig.add_trace(
                go.Scatter(x=x_vals, y=y_vals, mode='markers', name='Activity'),
                row=2, col=2
            )
        
        fig.update_layout(
            title=f"Persona Dashboard - {persona_data.get('name', 'User')}",
            height=800,
            showlegend=True
        )
        
        if output_path:
            fig.write_html(output_path)
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_persona_html_report(self, persona_data: Dict[str, Any], output_path: str = None) -> str:
        """Create a complete HTML report for the persona."""
        
        name = persona_data.get('name', 'Unknown User')
        username = persona_data.get('reddit_user', 'Unknown')
        analysis_score = persona_data.get('analysis_score', 0)
        personality_type = persona_data.get('personality_type', 'XXXX')
        quote = persona_data.get('quote', 'No quote available')
        
        # Generate charts
        personality_chart = self.create_personality_radar(persona_data)
        motivations_chart = self.create_motivations_bar(persona_data)
        traits_chart = self.create_traits_cloud(persona_data)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Persona Report - {name}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid #667eea;
                }}
                .header h1 {{
                    color: #667eea;
                    margin: 0;
                    font-size: 2.5em;
                }}
                .header p {{
                    color: #666;
                    margin: 5px 0;
                }}
                .score-badge {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 1.1em;
                }}
                .persona-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin: 30px 0;
                }}
                .persona-section {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #667eea;
                }}
                .persona-section h3 {{
                    color: #667eea;
                    margin-top: 0;
                }}
                .trait-list {{
                    list-style: none;
                    padding: 0;
                }}
                .trait-list li {{
                    background: white;
                    margin: 5px 0;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 3px solid #667eea;
                }}
                .quote-box {{
                    background: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 0 10px 10px 0;
                    font-style: italic;
                    font-size: 1.1em;
                }}
                .chart-container {{
                    margin: 20px 0;
                    text-align: center;
                }}
                .metadata {{
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 10px;
                    margin-top: 30px;
                    text-align: center;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Persona Report</h1>
                    <p><strong>User:</strong> {username}</p>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Personality Type:</strong> {personality_type}</p>
                    <p><strong>Analysis Score:</strong> <span class="score-badge">{analysis_score:.1f}%</span></p>
                </div>
                
                <div class="quote-box">
                    "{quote}"
                </div>
                
                <div class="persona-grid">
                    <div class="persona-section">
                        <h3>🎭 Personality Traits</h3>
                        <ul class="trait-list">
                            {chr(10).join([f'<li>{trait}</li>' for trait in persona_data.get('traits', [])])}
                        </ul>
                    </div>
                    
                    <div class="persona-section">
                        <h3>🎯 Goals</h3>
                        <ul class="trait-list">
                            {chr(10).join([f'<li>{goal}</li>' for goal in persona_data.get('goals', [])])}
                        </ul>
                    </div>
                    
                    <div class="persona-section">
                        <h3>⚠️ Frustrations</h3>
                        <ul class="trait-list">
                            {chr(10).join([f'<li>{frustration}</li>' for frustration in persona_data.get('frustrations', [])])}
                        </ul>
                    </div>
                    
                    <div class="persona-section">
                        <h3>📝 Behavior Habits</h3>
                        <ul class="trait-list">
                            {chr(10).join([f'<li>{habit}</li>' for habit in persona_data.get('behavior_habits', [])])}
                        </ul>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>📊 Personality Profile</h3>
                    {personality_chart if personality_chart else '<p>No personality data available</p>'}
                </div>
                
                <div class="chart-container">
                    <h3>🎯 Motivations</h3>
                    {motivations_chart if motivations_chart else '<p>No motivation data available</p>'}
                </div>
                
                <div class="chart-container">
                    <h3>🧠 Traits Distribution</h3>
                    {traits_chart if traits_chart else '<p>No traits data available</p>'}
                </div>
                
                <div class="metadata">
                    <p><strong>Generated by PersonaForge AI</strong></p>
                    <p>Powered by Advanced NLP & LLM Analysis</p>
                    <p>Generated at: {persona_data.get('metadata', {}).get('generated_at', 'Unknown')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    async def generate_all_visualizations(self, persona_data: Dict[str, Any], username: str) -> Dict[str, str]:
        """Generate all visualizations for a persona."""
        
        output_files = {}
        
        try:
            # Create individual charts
            personality_file = f"personas/{username}_personality_radar.html"
            personality_html = self.create_personality_radar(persona_data, personality_file)
            if personality_html:
                output_files['personality_radar'] = personality_file
            
            motivations_file = f"personas/{username}_motivations_bar.html"
            motivations_html = self.create_motivations_bar(persona_data, motivations_file)
            if motivations_html:
                output_files['motivations_bar'] = motivations_file
            
            traits_file = f"personas/{username}_traits_cloud.html"
            traits_html = self.create_traits_cloud(persona_data, traits_file)
            if traits_html:
                output_files['traits_cloud'] = traits_file
            
            # Create comprehensive dashboard
            dashboard_file = f"personas/{username}_dashboard.html"
            dashboard_html = self.create_comprehensive_dashboard(persona_data, dashboard_file)
            if dashboard_html:
                output_files['dashboard'] = dashboard_file
            
            # Create HTML report
            report_file = f"personas/{username}_report.html"
            report_html = self.create_persona_html_report(persona_data, report_file)
            if report_html:
                output_files['html_report'] = report_file
            
            logger.info(f"Generated {len(output_files)} visualizations for {username}")
            return output_files
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return {} 