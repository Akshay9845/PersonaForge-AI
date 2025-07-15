"""
PDF Generator Module
Creates comprehensive PDF reports for Reddit user personas.
"""

import os
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

class PDFGenerator:
    """Generates comprehensive PDF reports for Reddit user personas."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'CustomSubsection',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkgreen
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14
        )
        
        # Quote style
        self.quote_style = ParagraphStyle(
            'CustomQuote',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            rightIndent=20,
            fontName='Helvetica-Oblique',
            textColor=colors.grey
        )
    
    def create_chart_image(self, chart_data: Dict[str, Any], chart_type: str) -> Optional[bytes]:
        """Create chart images for the PDF."""
        try:
            if chart_type == "big_five":
                return self._create_big_five_chart(chart_data)
            elif chart_type == "personality_radar":
                return self._create_radar_chart(chart_data)
            elif chart_type == "interests_pie":
                return self._create_pie_chart(chart_data)
            elif chart_type == "activity_timeline":
                return self._create_timeline_chart(chart_data)
            elif chart_type == "sentiment_analysis":
                return self._create_sentiment_chart(chart_data)
            elif chart_type == "engagement_metrics":
                return self._create_engagement_chart(chart_data)
        except Exception as e:
            print(f"Error creating {chart_type} chart: {e}")
            return None
    
    def _create_big_five_chart(self, data: List[Dict[str, Any]]) -> bytes:
        """Create Big Five personality chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = [item['name'] for item in data]
        values = [item['value'] for item in data]
        colors_list = [item.get('color', '#1f77b4') for item in data]
        
        bars = ax.bar(names, values, color=colors_list, alpha=0.7)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Big Five Personality Traits', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{value:.0f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    
    def _create_radar_chart(self, data: List[Dict[str, Any]]) -> bytes:
        """Create personality radar chart."""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        names = [item['name'] for item in data]
        values = [item['value'] for item in data]
        
        # Close the plot by appending first value
        values += values[:1]
        names += names[:1]
        
        angles = [n / float(len(data)) * 2 * 3.14159 for n in range(len(data))]
        angles += angles[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#1f77b4')
        ax.fill(angles, values, alpha=0.25, color='#1f77b4')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(names[:-1])
        ax.set_ylim(0, 100)
        ax.set_title('Personality Radar Chart', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    
    def _create_pie_chart(self, data: List[Dict[str, Any]]) -> bytes:
        """Create interests pie chart."""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels = [item['name'] for item in data]
        sizes = [item['value'] for item in data]
        colors_list = plt.cm.Set3(range(len(labels)))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                         colors=colors_list, startangle=90)
        ax.set_title('Interest Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    
    def _create_timeline_chart(self, data: List[Dict[str, Any]]) -> bytes:
        """Create activity timeline chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = [item['name'] for item in data]
        values = [item['value'] for item in data]
        
        ax.plot(names, values, 'o-', linewidth=2, markersize=8, color='#2ecc71')
        ax.set_xlabel('Time Period', fontsize=12)
        ax.set_ylabel('Activity Level', fontsize=12)
        ax.set_title('Activity Timeline', fontsize=14, fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    
    def _create_sentiment_chart(self, data: List[Dict[str, Any]]) -> bytes:
        """Create sentiment analysis chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = [item['name'] for item in data]
        values = [item['value'] for item in data]
        colors_list = ['#e74c3c' if v < 0 else '#27ae60' if v > 0 else '#f39c12' for v in values]
        
        bars = ax.bar(names, values, color=colors_list, alpha=0.7)
        ax.set_ylabel('Sentiment Score', fontsize=12)
        ax.set_title('Sentiment Analysis', fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    
    def _create_engagement_chart(self, data: List[Dict[str, Any]]) -> bytes:
        """Create engagement metrics chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = [item['name'] for item in data]
        values = [item['value'] for item in data]
        
        bars = ax.bar(names, values, color='#3498db', alpha=0.7)
        ax.set_ylabel('Engagement Score', fontsize=12)
        ax.set_title('Engagement Metrics', fontsize=14, fontweight='bold')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    
    def generate_persona_pdf(self, persona_data: Dict[str, Any], output_path: str) -> str:
        """Generate a comprehensive PDF report for a Reddit user persona."""
        try:
            # Create the PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Add title page
            story.extend(self._create_title_page(persona_data))
            story.append(PageBreak())
            
            # Add executive summary
            story.extend(self._create_executive_summary(persona_data))
            story.append(PageBreak())
            
            # Add persona details
            story.extend(self._create_persona_details(persona_data))
            story.append(PageBreak())
            
            # Add personality analysis
            story.extend(self._create_personality_analysis(persona_data))
            story.append(PageBreak())
            
            # Add behavioral insights
            story.extend(self._create_behavioral_insights(persona_data))
            story.append(PageBreak())
            
            # Add Reddit activity
            story.extend(self._create_reddit_activity(persona_data))
            story.append(PageBreak())
            
            # Add charts and visualizations
            story.extend(self._create_charts_section(persona_data))
            story.append(PageBreak())
            
            # Add sample posts and comments
            story.extend(self._create_content_samples(persona_data))
            story.append(PageBreak())
            
            # Add technical details
            story.extend(self._create_technical_details(persona_data))
            
            # Build the PDF
            doc.build(story)
            
            return output_path
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise
    
    def _create_title_page(self, persona_data: Dict[str, Any]) -> List:
        """Create the title page."""
        elements = []
        
        # Title
        title = Paragraph(f"Reddit User Persona Analysis", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 30))
        
        # Username
        username = persona_data.get('reddit_username', 'Unknown User')
        username_para = Paragraph(f"<b>Username:</b> {username}", self.section_style)
        elements.append(username_para)
        elements.append(Spacer(1, 20))
        
        # Generated date
        generated_at = persona_data.get('generated_at', datetime.now().isoformat())
        date_para = Paragraph(f"<b>Generated:</b> {generated_at}", self.body_style)
        elements.append(date_para)
        elements.append(Spacer(1, 40))
        
        # Analysis score
        score = persona_data.get('analysis_score', 0)
        score_para = Paragraph(f"<b>Analysis Confidence Score:</b> {score}%", self.body_style)
        elements.append(score_para)
        
        return elements
    
    def _create_executive_summary(self, persona_data: Dict[str, Any]) -> List:
        """Create executive summary section."""
        elements = []
        
        # Section title
        title = Paragraph("Executive Summary", self.section_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Persona name and basic info
        name = persona_data.get('name', 'Unknown')
        age = persona_data.get('age', 'Unknown')
        occupation = persona_data.get('occupation', 'Unknown')
        location = persona_data.get('location', 'Unknown')
        
        summary_text = f"""
        This report presents a comprehensive analysis of Reddit user <b>{name}</b>, 
        a {age}-year-old {occupation} from {location}. The analysis is based on 
        their Reddit activity patterns, posting behavior, and community engagement.
        """
        
        summary_para = Paragraph(summary_text, self.body_style)
        elements.append(summary_para)
        elements.append(Spacer(1, 12))
        
        # Key insights
        elements.append(Paragraph("<b>Key Insights:</b>", self.subsection_style))
        
        # Get key traits
        traits = persona_data.get('traits', [])
        if traits:
            traits_text = f"<b>Personality Traits:</b> {', '.join(traits[:5])}"
            elements.append(Paragraph(traits_text, self.body_style))
            elements.append(Spacer(1, 6))
        
        # Get archetype
        archetype = persona_data.get('archetype', 'Unknown')
        archetype_text = f"<b>User Archetype:</b> {archetype}"
        elements.append(Paragraph(archetype_text, self.body_style))
        elements.append(Spacer(1, 6))
        
        # Get primary interests
        interests = persona_data.get('interests', [])
        if interests:
            interests_text = f"<b>Primary Interests:</b> {', '.join(interests[:3])}"
            elements.append(Paragraph(interests_text, self.body_style))
        
        return elements
    
    def _create_persona_details(self, persona_data: Dict[str, Any]) -> List:
        """Create persona details section."""
        elements = []
        
        # Section title
        title = Paragraph("Persona Details", self.section_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Create details table
        details_data = [
            ['Field', 'Value'],
            ['Name', persona_data.get('name', 'Unknown')],
            ['Age', persona_data.get('age', 'Unknown')],
            ['Occupation', persona_data.get('occupation', 'Unknown')],
            ['Location', persona_data.get('location', 'Unknown')],
            ['Status', persona_data.get('status', 'Unknown')],
            ['Tier', persona_data.get('tier', 'Unknown')],
            ['Archetype', persona_data.get('archetype', 'Unknown')],
        ]
        
        table = Table(details_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Quote
        quote = persona_data.get('quote', '')
        if quote:
            elements.append(Paragraph("<b>Representative Quote:</b>", self.subsection_style))
            quote_para = Paragraph(f'"{quote}"', self.quote_style)
            elements.append(quote_para)
        
        return elements
    
    def _create_personality_analysis(self, persona_data: Dict[str, Any]) -> List:
        """Create personality analysis section."""
        elements = []
        
        # Section title
        title = Paragraph("Personality Analysis", self.section_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Personality traits
        personality = persona_data.get('personality', {})
        if personality:
            elements.append(Paragraph("<b>Personality Dimensions:</b>", self.subsection_style))
            
            # Create personality table
            personality_data = [['Dimension', 'Score']]
            for trait, value in personality.items():
                personality_data.append([trait.title(), f"{value}%"])
            
            table = Table(personality_data, colWidths=[2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 12))
        
        # Motivations
        motivations = persona_data.get('motivations', {})
        if motivations:
            elements.append(Paragraph("<b>Motivations:</b>", self.subsection_style))
            
            motivation_data = [['Motivation', 'Score']]
            for motivation, value in motivations.items():
                motivation_data.append([motivation.replace('_', ' ').title(), f"{value}%"])
            
            table = Table(motivation_data, colWidths=[2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        return elements
    
    def _create_behavioral_insights(self, persona_data: Dict[str, Any]) -> List:
        """Create behavioral insights section."""
        elements = []
        
        # Section title
        title = Paragraph("Behavioral Insights", self.section_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Behavior habits
        habits = persona_data.get('behavior_habits', [])
        if habits:
            elements.append(Paragraph("<b>Behavior Habits:</b>", self.subsection_style))
            for habit in habits:
                habit_para = Paragraph(f"• {habit}", self.body_style)
                elements.append(habit_para)
            elements.append(Spacer(1, 12))
        
        # Frustrations
        frustrations = persona_data.get('frustrations', [])
        if frustrations:
            elements.append(Paragraph("<b>Frustrations:</b>", self.subsection_style))
            for frustration in frustrations:
                frustration_para = Paragraph(f"• {frustration}", self.body_style)
                elements.append(frustration_para)
            elements.append(Spacer(1, 12))
        
        # Goals and needs
        goals = persona_data.get('goals_needs', [])
        if goals:
            elements.append(Paragraph("<b>Goals & Needs:</b>", self.subsection_style))
            for goal in goals:
                goal_para = Paragraph(f"• {goal}", self.body_style)
                elements.append(goal_para)
        
        return elements
    
    def _create_reddit_activity(self, persona_data: Dict[str, Any]) -> List:
        """Create Reddit activity section."""
        elements = []
        
        # Section title
        title = Paragraph("Reddit Activity Analysis", self.section_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Activity patterns
        activity_patterns = persona_data.get('activity_patterns', {})
        if activity_patterns:
            elements.append(Paragraph("<b>Activity Patterns:</b>", self.subsection_style))
            
            activity_data = [['Pattern', 'Value']]
            for pattern, value in activity_patterns.items():
                activity_data.append([pattern.replace('_', ' ').title(), str(value)])
            
            table = Table(activity_data, colWidths=[2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 12))
        
        # Writing style
        writing_style = persona_data.get('writing_style', {})
        if writing_style:
            elements.append(Paragraph("<b>Writing Style:</b>", self.subsection_style))
            
            style_data = [['Aspect', 'Description']]
            for aspect, description in writing_style.items():
                style_data.append([aspect.replace('_', ' ').title(), str(description)])
            
            table = Table(style_data, colWidths=[1.5*inch, 3.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        return elements
    
    def _create_charts_section(self, persona_data: Dict[str, Any]) -> List:
        """Create charts and visualizations section."""
        elements = []
        
        # Section title
        title = Paragraph("Charts & Visualizations", self.section_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Get chart data
        chart_data = persona_data.get('chart_data', {})
        
        # Big Five Chart
        if 'big_five' in chart_data and chart_data['big_five']:
            elements.append(Paragraph("<b>Big Five Personality Traits:</b>", self.subsection_style))
            big_five_img = self.create_chart_image(chart_data['big_five'], 'big_five')
            if big_five_img:
                img = Image(io.BytesIO(big_five_img), width=6*inch, height=3.5*inch)
                elements.append(img)
            elements.append(Spacer(1, 12))
        
        # Personality Radar Chart
        if 'personality_radar' in chart_data and chart_data['personality_radar']:
            elements.append(Paragraph("<b>Personality Radar Chart:</b>", self.subsection_style))
            radar_img = self.create_chart_image(chart_data['personality_radar'], 'personality_radar')
            if radar_img:
                img = Image(io.BytesIO(radar_img), width=5*inch, height=5*inch)
                elements.append(img)
            elements.append(Spacer(1, 12))
        
        # Interests Pie Chart
        if 'interests_pie' in chart_data and chart_data['interests_pie']:
            elements.append(Paragraph("<b>Interest Distribution:</b>", self.subsection_style))
            pie_img = self.create_chart_image(chart_data['interests_pie'], 'interests_pie')
            if pie_img:
                img = Image(io.BytesIO(pie_img), width=5*inch, height=5*inch)
                elements.append(img)
            elements.append(Spacer(1, 12))
        
        # Activity Timeline
        if 'activity_timeline' in chart_data and chart_data['activity_timeline']:
            elements.append(Paragraph("<b>Activity Timeline:</b>", self.subsection_style))
            timeline_img = self.create_chart_image(chart_data['activity_timeline'], 'activity_timeline')
            if timeline_img:
                img = Image(io.BytesIO(timeline_img), width=6*inch, height=3.5*inch)
                elements.append(img)
            elements.append(PageBreak())
        
        return elements
    
    def _create_content_samples(self, persona_data: Dict[str, Any]) -> List:
        """Create sample posts and comments section."""
        elements = []
        
        # Section title
        title = Paragraph("Sample Reddit Content", self.section_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Real posts
        real_posts = persona_data.get('real_posts', [])
        if real_posts:
            elements.append(Paragraph("<b>Sample Posts:</b>", self.subsection_style))
            elements.append(Spacer(1, 6))
            
            for i, post in enumerate(real_posts[:5], 1):  # Limit to 5 posts
                post_title = post.get('title', 'No title')
                subreddit = post.get('subreddit', 'unknown')
                score = post.get('score', 0)
                content = post.get('content', '')[:200] + '...' if len(post.get('content', '')) > 200 else post.get('content', '')
                
                post_text = f"""
                <b>{i}. {post_title}</b><br/>
                <i>r/{subreddit} • Score: {score}</i><br/>
                {content}
                """
                
                post_para = Paragraph(post_text, self.body_style)
                elements.append(post_para)
                elements.append(Spacer(1, 8))
        
        elements.append(Spacer(1, 12))
        
        # Real comments
        real_comments = persona_data.get('real_comments', [])
        if real_comments:
            elements.append(Paragraph("<b>Sample Comments:</b>", self.subsection_style))
            elements.append(Spacer(1, 6))
            
            for i, comment in enumerate(real_comments[:5], 1):  # Limit to 5 comments
                subreddit = comment.get('subreddit', 'unknown')
                score = comment.get('score', 0)
                content = comment.get('content', '')[:200] + '...' if len(comment.get('content', '')) > 200 else comment.get('content', '')
                
                comment_text = f"""
                <b>{i}. Comment in r/{subreddit}</b><br/>
                <i>Score: {score}</i><br/>
                {content}
                """
                
                comment_para = Paragraph(comment_text, self.body_style)
                elements.append(comment_para)
                elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_technical_details(self, persona_data: Dict[str, Any]) -> List:
        """Create technical details section."""
        elements = []
        
        # Section title
        title = Paragraph("Technical Details", self.section_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Analysis metadata
        elements.append(Paragraph("<b>Analysis Metadata:</b>", self.subsection_style))
        
        metadata_data = [
            ['Field', 'Value'],
            ['Analysis Score', f"{persona_data.get('analysis_score', 0)}%"],
            ['Generated At', persona_data.get('generated_at', 'Unknown')],
            ['Data Source', 'Reddit API + Web Scraping'],
            ['Analysis Method', 'AI-Powered Personality Analysis'],
            ['Confidence Level', 'High' if persona_data.get('analysis_score', 0) > 70 else 'Medium' if persona_data.get('analysis_score', 0) > 40 else 'Low'],
        ]
        
        table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Footer
        footer_text = """
        <i>This report was generated by PersonaForge AI - Intelligent Reddit User Analysis Platform.
        The analysis is based on publicly available Reddit data and should be used for research and 
        understanding purposes only.</i>
        """
        
        footer_para = Paragraph(footer_text, self.body_style)
        elements.append(footer_para)
        
        return elements 