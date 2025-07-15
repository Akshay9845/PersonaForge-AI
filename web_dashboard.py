"""
Web Dashboard Module
Provides FastAPI web interface and REST API for Reddit Persona AI.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles
from dotenv import load_dotenv
import traceback
import io

from scraper import RedditScraper
from analyzer import PersonaAnalyzer
from persona_builder import PersonaBuilder
from visualizer import PersonaVisualizer
from pdf_generator import PDFGenerator
from utils import create_output_dir, extract_reddit_username

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Create static directory if it doesn't exist
Path("static").mkdir(exist_ok=True)
Path("static/css").mkdir(exist_ok=True)
Path("static/js").mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Reddit Persona AI",
    description="Intelligent User Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for API
class UserAnalysisRequest(BaseModel):
    username: str
    max_posts: int = 25  # Increased from 5 to 25
    max_comments: int = 30  # Increased from 10 to 30
    save_json: bool = True
    generate_pdf: bool = False
    save_visualizations: bool = True

class ComparisonRequest(BaseModel):
    user1: str
    user2: str
    max_posts: Optional[int] = None
    max_comments: Optional[int] = None

class AnalysisResponse(BaseModel):
    username: str
    status: str
    persona: Optional[Dict[str, Any]] = None
    visualizations: Optional[List[str]] = None
    error: Optional[str] = None
    generated_at: str

# Global instances (except scraper which needs to be created per request)
analyzer = PersonaAnalyzer()
builder = PersonaBuilder()
visualizer = PersonaVisualizer()
pdf_generator = PDFGenerator()

# Analysis results cache
analysis_cache = {}

SHOW_DEBUG = os.getenv("ENV") == "development"

def clean_username(username):
    # Remove 'u/' or 'r/' prefix if present
    if username.startswith('u/') or username.startswith('r/'):
        return username[2:]
    return username

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the enhanced dashboard page."""
    return FileResponse("static/enhanced-dashboard.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the enhanced dashboard page."""
    return FileResponse("static/enhanced-dashboard.html")

@app.get("/legacy", response_class=HTMLResponse)
async def legacy_dashboard():
    """Serve the legacy web interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reddit Persona AI - Intelligent User Analysis</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                color: white;
            }
            
            .header h1 {
                font-size: 3rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .main-content {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            .analysis-form {
                max-width: 600px;
                margin: 0 auto;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #555;
            }
            
            .form-group input, .form-group select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            
            .form-group input:focus, .form-group select:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .checkbox-group {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }
            
            .checkbox-item {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .checkbox-item input[type="checkbox"] {
                width: auto;
            }
            
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
                width: 100%;
            }
            
            .btn:hover {
                transform: translateY(-2px);
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .results {
                margin-top: 40px;
                display: none;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                display: none;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                display: none;
            }
            
            .success {
                background: #efe;
                color: #363;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                display: none;
            }
            
            .features {
                margin-top: 40px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            
            .feature-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            
            .feature-card h3 {
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .api-section {
                margin-top: 40px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            
            .api-section h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .code-block {
                background: #2d3748;
                color: #e2e8f0;
                padding: 15px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                overflow-x: auto;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Reddit Persona AI</h1>
                <p>Intelligent User Analysis Platform</p>
            </div>
            
            <div class="main-content">
                <div class="analysis-form">
                    <h2 style="text-align: center; margin-bottom: 30px; color: #667eea;">Analyze Reddit User</h2>
                    
                    <form id="analysisForm">
                        <div class="form-group">
                            <label for="username">Reddit Username:</label>
                            <input type="text" id="username" name="username" placeholder="e.g., kojied" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="maxPosts">Maximum Posts:</label>
                            <select id="maxPosts" name="maxPosts">
                                <option value="20">20</option>
                                <option value="50" selected>50</option>
                                <option value="100">100</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="maxComments">Maximum Comments:</label>
                            <select id="maxComments" name="maxComments">
                                <option value="20">20</option>
                                <option value="50" selected>50</option>
                                <option value="100">100</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Options:</label>
                            <div class="checkbox-group">
                                <div class="checkbox-item">
                                    <input type="checkbox" id="saveJson" name="saveJson" checked>
                                    <label for="saveJson">Save JSON</label>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox" id="generatePdf" name="generatePdf">
                                    <label for="generatePdf">Generate PDF</label>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox" id="saveViz" name="saveViz" checked>
                                    <label for="saveViz">Save Visualizations</label>
                                </div>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn" id="analyzeBtn">🔍 Analyze User</button>
                    </form>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p>Analyzing user data... This may take a few minutes.</p>
                    </div>
                    
                    <div class="error" id="error"></div>
                    <div class="success" id="success"></div>
                    
                    <div class="results" id="results">
                        <h3>Analysis Results</h3>
                        <div id="resultsContent"></div>
                    </div>
                </div>
                
                <div class="features">
                    <div class="feature-card">
                        <h3>🤖 AI-Powered Analysis</h3>
                        <p>Advanced NLP and GPT-4 integration for deep insights</p>
                    </div>
                    <div class="feature-card">
                        <h3>📊 Interactive Visualizations</h3>
                        <p>Beautiful charts and graphs for data exploration</p>
                    </div>
                    <div class="feature-card">
                        <h3>🔍 Citation System</h3>
                        <p>Every insight backed by specific Reddit posts/comments</p>
                    </div>
                    <div class="feature-card">
                        <h3>📄 Multiple Formats</h3>
                        <p>Export as text, JSON, PDF, and interactive HTML</p>
                    </div>
                </div>
                
                <div class="api-section">
                    <h3>🔌 REST API</h3>
                    <p>Use our API for programmatic access:</p>
                    <div class="code-block">
POST /api/analyze
{
  "username": "kojied",
  "max_posts": null,
  "max_comments": null
}
                    </div>
                    <p><a href="/docs" style="color: #667eea;">View API Documentation</a></p>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('analysisForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const maxPosts = parseInt(document.getElementById('maxPosts').value);
                const maxComments = parseInt(document.getElementById('maxComments').value);
                const saveJson = document.getElementById('saveJson').checked;
                const generatePdf = document.getElementById('generatePdf').checked;
                const saveViz = document.getElementById('saveViz').checked;
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                document.getElementById('success').style.display = 'none';
                document.getElementById('results').style.display = 'none';
                document.getElementById('analyzeBtn').disabled = true;
                
                try {
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            username: username,
                            max_posts: maxPosts,
                            max_comments: maxComments,
                            save_json: saveJson,
                            generate_pdf: generatePdf,
                            save_visualizations: saveViz
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('success').style.display = 'block';
                        document.getElementById('success').textContent = `Analysis completed successfully! Persona saved to: ${result.persona_file}`;
                        
                        // Show results
                        document.getElementById('results').style.display = 'block';
                        document.getElementById('resultsContent').innerHTML = `
                            <p><strong>Personality:</strong> ${result.persona.personality.type}</p>
                            <p><strong>Top Interests:</strong> ${result.persona.interests.join(', ')}</p>
                            <p><strong>Writing Style:</strong> ${result.persona.writing_style.summary}</p>
                            <p><strong>Confidence:</strong> ${(result.persona.metadata.confidence_overall * 100).toFixed(1)}%</p>
                        `;
                    } else {
                        throw new Error(result.error || 'Analysis failed');
                    }
                    
                } catch (error) {
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').textContent = `Error: ${error.message}`;
                } finally {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('analyzeBtn').disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_user(request: UserAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a Reddit user and generate persona."""
    extracted_username = None
    try:
        # Extract username from input (handles URLs, usernames, etc.)
        logger.info(f"Original username input: {request.username}")
        extracted_username = extract_reddit_username(request.username)
        logger.info(f"Extracted clean username: {extracted_username}")
        if not extracted_username:
            raise HTTPException(status_code=400, detail="Invalid Reddit username or URL format")
        
        logger.info(f"Starting analysis for user: {extracted_username} (original input: {request.username})")
        
        # Create output directory
        output_dir = "personas"
        create_output_dir(output_dir)
        
        # Perform analysis with proper cleanup
        scraper = RedditScraper()
        async with scraper:
            user_data = await scraper.scrape_user(extracted_username, request.max_posts, request.max_comments)
        
        if not user_data['posts'] and not user_data['comments']:
            logger.warning(f"No data collected for user {extracted_username} from any source")
            # Instead of raising an error, create a template persona
            logger.info("Creating template persona for user with no data")
            from llm_service import LLMService
            llm_service = LLMService()
            persona = llm_service._generate_template_persona(user_data, {})
            analysis_results = {}
        else:
            analysis_results = await analyzer.analyze_user(user_data)
            persona = await builder.build_persona(user_data, analysis_results)
        persona = await builder.build_persona(user_data, analysis_results)
        
        # Save persona
        persona_file = f"{output_dir}/{extracted_username}_persona.txt"
        async with aiofiles.open(persona_file, 'w', encoding='utf-8') as f:
            await f.write(persona['formatted_text'])
        
        # Save JSON if requested
        json_file = None
        if request.save_json:
            json_file = f"{output_dir}/{extracted_username}_persona.json"
            async with aiofiles.open(json_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(persona, indent=2, ensure_ascii=False))
        
        # Generate visualizations if requested
        viz_files = []
        chart_data = {}
        if request.save_visualizations:
            try:
                # Generate chart data for frontend
                chart_data = await generate_chart_data(persona)
                
                # Try to generate HTML visualizations (optional)
                try:
                    viz_files = await visualizer.create_visualizations(persona, output_dir)
                except Exception as viz_error:
                    logger.warning(f"HTML visualization generation failed: {viz_error}")
                    # Continue without HTML visualizations
                
            except Exception as viz_error:
                logger.error(f"Chart data generation failed: {viz_error}")
                logger.error("Chart generation traceback:\n" + traceback.format_exc())
                # Continue without visualizations
        
        # Generate PDF if requested
        pdf_file = None
        if request.generate_pdf:
            try:
                # Use the same PDF generator as the download endpoint
                output_dir_path = Path(output_dir)
                pdf_path = output_dir_path / f"{extracted_username}_comprehensive_report.pdf"
                pdf_generator.generate_persona_pdf(persona, str(pdf_path))
                pdf_file = str(pdf_path)
                logger.info(f"PDF generated successfully: {pdf_file}")
            except Exception as e:
                logger.warning(f"PDF generation failed: {e}")
                pdf_file = None
        
        # Add chart data to persona
        if chart_data:
            persona['chart_data'] = chart_data
        
        # After extracting clean_username from extract_reddit_username
        normalized_username = clean_username(extracted_username)
        # Cache results
        analysis_cache[normalized_username] = {
            'persona': persona,
            'generated_at': datetime.now().isoformat(),
            'files': {
                'persona': persona_file,
                'json': json_file,
                'pdf': pdf_file,
                'visualizations': viz_files
            }
        }
        
        return AnalysisResponse(
            username=normalized_username,
            status="completed",
            persona=persona,
            visualizations=viz_files,
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except Exception as e:
        username_for_error = extracted_username if extracted_username else request.username
        logger.error(f"Analysis failed for {username_for_error}: {e}")
        logger.error("Traceback:\n" + traceback.format_exc())
        detail = str(e) if SHOW_DEBUG else "Internal server error"
        raise HTTPException(status_code=500, detail=detail)


async def generate_chart_data(persona: Dict[str, Any]) -> Dict[str, Any]:
    """Generate chart data for frontend visualization."""
    chart_data = {}
    try:
        # Big Five (OCEAN) Personality Chart
        personality = persona.get('personality', {})
        big_five_data = []
        if personality:
            big_five_mapping = {
                'openness': personality.get('openness', 0),
                'conscientiousness': personality.get('conscientiousness', 0),
                'extraversion': personality.get('extraversion', 0),
                'agreeableness': personality.get('agreeableness', 0),
                'neuroticism': personality.get('neuroticism', 0)
            }
            if not any(big_five_mapping.values()):
                introvert = personality.get('introvert', 50)
                extrovert = personality.get('extrovert', 50)
                intuition = personality.get('intuition', 50)
                sensing = personality.get('sensing', 50)
                feeling = personality.get('feeling', 50)
                thinking = personality.get('thinking', 50)
                perceiving = personality.get('perceiving', 50)
                judging = personality.get('judging', 50)
                big_five_mapping = {
                    'openness': intuition,
                    'conscientiousness': judging,
                    'extraversion': extrovert,
                    'agreeableness': feeling,
                    'neuroticism': max(0, 100 - (introvert + extrovert) // 2)
                }
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            for i, (trait, value) in enumerate(big_five_mapping.items()):
                if value > 0:
                    big_five_data.append({'name': trait.capitalize(), 'value': int(value), 'color': colors[i % len(colors)]})
        chart_data['big_five'] = big_five_data
        # Personality Radar Chart
        radar_data = []
        if personality:
            radar_dimensions = [
                ('Introvert', personality.get('introvert', 0)),
                ('Extrovert', personality.get('extrovert', 0)),
                ('Intuition', personality.get('intuition', 0)),
                ('Sensing', personality.get('sensing', 0)),
                ('Feeling', personality.get('feeling', 0)),
                ('Thinking', personality.get('thinking', 0))
            ]
            for name, value in radar_dimensions:
                if value and value > 0:
                    radar_data.append({'name': name, 'value': int(value)})
        chart_data['personality_radar'] = radar_data
        # Interests Pie Chart
        interests = persona.get('interests', [])
        interests_pie = []
        if interests:
            if isinstance(interests, list):
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                for i, interest in enumerate(interests[:8]):
                    interests_pie.append({'name': str(interest).capitalize(), 'value': max(1, 100 // len(interests)), 'color': colors[i % len(colors)]})
            elif isinstance(interests, dict) and 'interest_scores' in interests:
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                for i, (interest, score) in enumerate(interests['interest_scores'].items()):
                    if score > 0:
                        interests_pie.append({'name': interest.capitalize(), 'value': int(score * 100), 'color': colors[i % len(colors)]})
            elif isinstance(interests, dict):
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
                for i, (interest, score) in enumerate(interests.items()):
                    if isinstance(score, (int, float)) and score > 0:
                        interests_pie.append({'name': str(interest).capitalize(), 'value': int(score * 100) if isinstance(score, float) else int(score), 'color': colors[i % len(colors)]})
        chart_data['interests_pie'] = interests_pie
        # Motivations Bar Chart
        motivations = persona.get('motivations', {})
        motivations_data = []
        if motivations:
            for i, (motivation, value) in enumerate(motivations.items()):
                if isinstance(value, (int, float)) and value > 0:
                    motivations_data.append({'name': motivation.replace('_', ' ').title(), 'value': int(value)})
        chart_data['motivations'] = motivations_data
        # Community Engagement Bar Chart
        engagement = persona.get('community_engagement', {})
        if not engagement and 'engagement_metrics' in persona:
            engagement = persona['engagement_metrics']
        engagement_data = []
        if engagement:
            # Handle different engagement data structures
            if 'total_posts' in engagement or 'total_comments' in engagement:
                # Legacy structure with total counts
                engagement_items = [
                    ('posts', engagement.get('total_posts', 0)),
                    ('comments', engagement.get('total_comments', 0)),
                    ('karma', engagement.get('total_karma', 0)),
                    ('upvotes', engagement.get('total_upvotes', 0)),
                    ('downvotes', engagement.get('total_downvotes', 0))
                ]
            else:
                # New structure with metrics
                engagement_items = [
                    ('subreddit_diversity', engagement.get('subreddit_diversity', 0)),
                    ('avg_score', int(engagement.get('avg_score', 0) * 10)),  # Scale up for visibility
                    ('engagement_level', engagement.get('level', 'low'))
                ]
            for name, value in engagement_items:
                if isinstance(value, (int, float)) and value > 0:
                    engagement_data.append({'name': name.replace('_', ' ').title(), 'value': int(value)})
        chart_data['community_engagement'] = engagement_data
        # Activity Patterns Bar Chart
        activity = persona.get('activity_patterns', {})
        activity_data = []
        if activity:
            # Handle different activity data structures
            if 'morning_activity' in activity or 'afternoon_activity' in activity:
                # Legacy structure with time-based activity
                activity_items = [
                    ('morning', activity.get('morning_activity', 0)),
                    ('afternoon', activity.get('afternoon_activity', 0)),
                    ('evening', activity.get('evening_activity', 0)),
                    ('night', activity.get('night_activity', 0)),
                    ('weekend', activity.get('weekend_activity', 0))
                ]
            else:
                # New structure with pattern data
                pattern = activity.get('pattern', 'unknown')
                peak_hour = activity.get('peak_hour', 12)
                frequency = activity.get('frequency', 1.0)
                activity_items = [
                    ('pattern', pattern),
                    ('peak_hour', peak_hour),
                    ('frequency', int(frequency * 10))  # Scale up for visibility
                ]
            for name, value in activity_items:
                if isinstance(value, (int, float)) and value > 0:
                    activity_data.append({'name': name.replace('_', ' ').title(), 'value': int(value)})
        chart_data['activity_patterns'] = activity_data
        # Real Posts and Comments for display
        real_posts = persona.get('real_posts', [])
        real_comments = persona.get('real_comments', [])
        chart_data['real_content'] = {'posts': real_posts[:3] if real_posts else [], 'comments': real_comments[:3] if real_comments else []}
        # Sentiment Timeline (simplified)
        sentiment_data = persona.get('sentiment', {})
        timeline_data = []
        if sentiment_data:
            if isinstance(sentiment_data, dict) and 'timeline' in sentiment_data:
                for entry in sentiment_data['timeline'][:10]:
                    if isinstance(entry, dict):
                        timeline_data.append({'name': str(entry.get('date', 'Unknown')), 'value': int(entry.get('sentiment', 0))})
            else:
                overall_sentiment = sentiment_data.get('score', 0)
                timeline_data = [
                    {'name': 'Jan', 'value': int(overall_sentiment * 100)},
                    {'name': 'Feb', 'value': int(overall_sentiment * 100)},
                    {'name': 'Mar', 'value': int(overall_sentiment * 100)},
                    {'name': 'Apr', 'value': int(overall_sentiment * 100)},
                    {'name': 'May', 'value': int(overall_sentiment * 100)},
                    {'name': 'Jun', 'value': int(overall_sentiment * 100)}
                ]
        chart_data['sentiment_timeline'] = timeline_data
        # Always output all keys
        for key in ['big_five', 'personality_radar', 'interests_pie', 'motivations', 'community_engagement', 'activity_patterns', 'real_content', 'sentiment_timeline']:
            if key not in chart_data:
                chart_data[key] = [] if key != 'real_content' else {'posts': [], 'comments': []}
        return chart_data
    except Exception as e:
        logger.error(f"Error generating chart data: {e}")
        logger.error("Chart data generation traceback:\n" + traceback.format_exc())
        # Always output all keys even on error
        for key in ['big_five', 'personality_radar', 'interests_pie', 'motivations', 'community_engagement', 'activity_patterns', 'real_content', 'sentiment_timeline']:
            if key not in chart_data:
                chart_data[key] = [] if key != 'real_content' else {'posts': [], 'comments': []}
        return chart_data


@app.post("/api/compare")
async def compare_users(request: ComparisonRequest):
    """Compare two Reddit users."""
    
    try:
        # Extract usernames from input
        clean_user1 = extract_reddit_username(request.user1)
        clean_user2 = extract_reddit_username(request.user2)
        
        if not clean_user1 or not clean_user2:
            raise HTTPException(status_code=400, detail="Invalid Reddit username or URL format")
        
        logger.info(f"Comparing users: {clean_user1} vs {clean_user2} (original: {request.user1} vs {request.user2})")
        
        # Analyze both users with proper cleanup
        scraper = RedditScraper()
        async with scraper:
            user1_data = await scraper.scrape_user(clean_user1, request.max_posts, request.max_comments)
            user2_data = await scraper.scrape_user(clean_user2, request.max_posts, request.max_comments)
        
        user1_analysis = await analyzer.analyze_user(user1_data)
        user2_analysis = await analyzer.analyze_user(user2_data)
        
        user1_persona = await builder.build_persona(user1_data, user1_analysis)
        user2_persona = await builder.build_persona(user2_data, user2_analysis)
        
        # Generate comparison
        comparison = await builder.compare_personas(user1_persona, user2_persona)
        
        # Save comparison
        output_dir = "personas"
        create_output_dir(output_dir)
        comparison_file = f"{output_dir}/comparison_{clean_user1}_vs_{clean_user2}.txt"
        
        async with aiofiles.open(comparison_file, 'w', encoding='utf-8') as f:
            await f.write(comparison['formatted_text'])
        
        return {
            "user1": clean_user1,
            "user2": clean_user2,
            "comparison": comparison,
            "comparison_file": comparison_file,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/persona/{username}")
async def get_persona(username: str):
    """Get cached persona for a user."""
    
    if username not in analysis_cache:
        raise HTTPException(status_code=404, detail="Persona not found. Please analyze the user first.")
    
    return analysis_cache[username]


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/generate-persona")
async def generate_persona(request: UserAnalysisRequest):
    """Generate a complete enhanced persona for a Reddit user."""
    try:
        # Extract username from input (handles URLs, usernames, etc.)
        logger.info(f"Original username input: {request.username}")
        clean_username = extract_reddit_username(request.username)
        logger.info(f"Extracted clean username: {clean_username}")
        if not clean_username:
            return {"success": False, "error": "Invalid Reddit username or URL format"}
        
        scraper = RedditScraper()
        async with scraper:
            user_data = await scraper.scrape_user(clean_username, request.max_posts, request.max_comments)
        
        analyzer = PersonaAnalyzer()
        analysis_results = await analyzer.analyze_user(user_data)
        
        builder = PersonaBuilder()
        persona_data = await builder.build_persona(user_data, analysis_results)
        
        # Generate visualizations
        output_dir = create_output_dir(clean_username)
        viz_files = await visualizer.create_visualizations(persona_data, str(output_dir))
        
        return {
            "success": True,
            "persona": persona_data,
            "visualizations": viz_files
        }
    except Exception as e:
        logger.error(f"Error generating persona: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/demo-persona")
async def get_demo_persona():
    """Get a demo persona for showcasing the system."""
    try:
        from enhanced_persona_schema import create_sample_persona
        from visualizer import PersonaVisualizer
        
        # Create a rich demo persona
        persona = create_sample_persona()
        persona.username = "demo_user"
        persona.reddit_user = "u/demo_user"
        persona.age = 28
        persona.gender = "Female"
        persona.occupation = "Software Engineer"
        persona.status = "In a relationship"
        persona.location = "San Francisco, CA"
        persona.tier = "Early Adopter"
        persona.archetype = "The Creator"
        persona.traits = ["Analytical", "Creative", "Detail-oriented", "Problem-solver", "Tech-savvy"]
        
        # Rich motivations
        persona.motivations.convenience = 85
        persona.motivations.wellness = 70
        persona.motivations.speed = 90
        persona.motivations.preferences = 75
        persona.motivations.comfort = 60
        persona.motivations.dietary_needs = 80
        persona.motivations.privacy = 65
        persona.motivations.community = 45
        persona.motivations.learning = 95
        persona.motivations.entertainment = 55
        
        # Rich personality
        persona.personality.introvert = 70
        persona.personality.extrovert = 30
        persona.personality.intuition = 60
        persona.personality.sensing = 40
        persona.personality.feeling = 35
        persona.personality.thinking = 65
        persona.personality.perceiving = 45
        persona.personality.judging = 55
        
        # Rich behavior and goals
        persona.behavior_habits = [
            "Spends 2-3 hours daily on Reddit tech communities",
            "Prefers asynchronous communication over meetings",
            "Uses multiple productivity apps and tools",
            "Regularly contributes to open-source projects",
            "Follows a structured daily routine"
        ]
        
        persona.frustrations = [
            "Too many meetings interrupting deep work",
            "Lack of clear documentation in projects",
            "Slow response times from team members",
            "Inconsistent coding standards across teams",
            "Difficulty finding reliable tech solutions"
        ]
        
        persona.goals = [
            "Master advanced programming concepts",
            "Build a successful side project",
            "Improve work-life balance",
            "Contribute to meaningful open-source projects",
            "Develop leadership skills in tech"
        ]
        
        persona.quote = "I believe in building things that matter. Every line of code should serve a purpose and every feature should solve a real problem for real users."
        persona.personality_type = "INTJ"
        persona.analysis_score = 94
        
        # Add data sources
        persona.data_sources = [
            {
                "type": "post",
                "text": "Just shipped a new feature that reduces API response time by 40%. The feeling of solving complex problems is what keeps me coding.",
                "url": "https://reddit.com/r/programming/comments/example1",
                "subreddit": "programming"
            },
            {
                "type": "comment",
                "text": "I've found that the best way to learn is by building real projects. Theory is important, but nothing beats hands-on experience.",
                "url": "https://reddit.com/r/learnprogramming/comments/example2",
                "subreddit": "learnprogramming"
            },
            {
                "type": "post",
                "text": "Working remotely has been a game-changer for my productivity. Fewer interruptions mean more time for deep work.",
                "url": "https://reddit.com/r/remotework/comments/example3",
                "subreddit": "remotework"
            }
        ]
        
        persona.interests = ["Software Development", "Productivity", "Open Source", "Tech News", "Problem Solving"]
        persona.writing_style = {
            "summary": "Clear, technical, and solution-oriented",
            "complexity": "Moderate to Complex",
            "tone": "Professional but approachable"
        }
        persona.social_views = [
            "Technology should empower people",
            "Open source is the future of software",
            "Continuous learning is essential in tech"
        ]
        persona.activity_patterns = {
            "frequency": "Daily",
            "peak_hours": "Evenings and weekends",
            "engagement_style": "Thoughtful, detailed responses"
        }
        
        persona.calculate_analysis_score()
        persona_data = persona.to_dict()
        
        # Generate visualizations
        output_dir = create_output_dir("demo_user")
        viz_files = await visualizer.create_visualizations(persona_data, str(output_dir))
        
        return {
            "success": True,
            "persona": persona_data,
            "visualizations": viz_files
        }
    except Exception as e:
        logger.error(f"Error generating demo persona: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/files/{username}")
async def get_persona_files(username: str):
    """Get all files generated for a user."""
    
    if username not in analysis_cache:
        raise HTTPException(status_code=404, detail="Files not found")
    
    files = analysis_cache[username]['files']
    
    # Check which files exist
    existing_files = {}
    for file_type, file_path in files.items():
        if file_path and Path(file_path).exists():
            existing_files[file_type] = file_path
    
    return {
        "username": username,
        "files": existing_files,
        "generated_at": analysis_cache[username]['generated_at']
    }


@app.get("/download/{file_type}/{username}")
async def download_file(file_type: str, username: str):
    """Download generated files."""
    
    if username not in analysis_cache:
        raise HTTPException(status_code=404, detail="Files not found")
    
    files = analysis_cache[username]['files']
    file_path = files.get(file_type)
    
    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=Path(file_path).name,
        media_type='application/octet-stream'
    )


@app.get("/download/pdf/{username}")
async def download_pdf(username: str):
    """Download comprehensive PDF report for a user."""
    
    username = clean_username(username)
    if username not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        # Look for PDF in the personas directory first (where analysis endpoint creates it)
        personas_dir = Path("personas")
        pdf_path = personas_dir / f"{username}_comprehensive_report.pdf"
        
        # If not found in personas, check in username-specific directory
        if not pdf_path.exists():
            output_dir = create_output_dir(username)
            pdf_path = output_dir / f"{username}_comprehensive_report.pdf"
        
        # Check if PDF already exists
        if not pdf_path.exists():
            # Generate PDF if it doesn't exist
            persona_data = analysis_cache[username]['persona']
            pdf_generator.generate_persona_pdf(persona_data, str(pdf_path))
        
        # Return the PDF file
        return FileResponse(
            path=str(pdf_path),
            filename=f"{username}_persona_report.pdf",
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error downloading PDF for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading PDF: {str(e)}")


@app.post("/api/generate-pdf/{username}")
async def generate_pdf_api(username: str):
    """API endpoint to generate PDF report."""
    
    if username not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        # Get the persona data
        persona_data = analysis_cache[username]['persona']
        
        # Create output directory
        output_dir = create_output_dir(username)
        pdf_path = output_dir / f"{username}_comprehensive_report.pdf"
        
        # Generate PDF
        pdf_generator.generate_persona_pdf(persona_data, str(pdf_path))
        
        return {
            "success": True,
            "message": "PDF generated successfully",
            "pdf_path": str(pdf_path),
            "download_url": f"/download/pdf/{username}"
        }
        
    except Exception as e:
        logger.error(f"Error generating PDF for {username}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/extract-username")
async def extract_username_api(request: Request):
    """Debug endpoint to extract Reddit username from input."""
    data = await request.json()
    input_text = data.get("input", "")
    extracted = extract_reddit_username(input_text)
    return {"input": input_text, "extracted_username": extracted}


class WebDashboard:
    """Web dashboard manager."""
    
    def __init__(self):
        """Initialize the web dashboard."""
        self.app = app
    
    def start(self, host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
        """Start the web dashboard."""
        logger.info(f"Starting web dashboard on {host}:{port}")
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )


def start_api_server(host: str = "0.0.0.0", port: int = 8000, workers: int = 4):
    """Start the API server."""
    logger.info(f"Starting API server on {host}:{port} with {workers} workers")
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        log_level="info"
    )


if __name__ == "__main__":
    # Start the web dashboard
    dashboard = WebDashboard()
    dashboard.start() 