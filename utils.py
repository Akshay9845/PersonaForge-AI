"""
Utility Functions Module
Helper functions for logging, file operations, PDF generation, and configuration.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import aiofiles
from jinja2 import Template
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def setup_logging(level: str = None):
    """Setup logging configuration."""
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "persona_ai.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger.info(f"Logging configured with level: {level}")


def create_output_dir(directory: str) -> Path:
    """Create output directory if it doesn't exist."""
    output_path = Path(directory)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory created/verified: {output_path}")
    return output_path


def load_config(config_file: str = ".env") -> Dict[str, Any]:
    """Load configuration from environment file."""
    config = {}
    
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
        
        logger.info(f"Configuration loaded from {config_file}")
        return config
        
    except FileNotFoundError:
        logger.warning(f"Configuration file {config_file} not found")
        return {}
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}


async def generate_pdf_report(persona: Dict[str, Any], output_dir: str) -> str:
    """Generate a professional PDF report from persona data."""
    
    if not WEASYPRINT_AVAILABLE:
        logger.warning("WeasyPrint not available. PDF generation disabled.")
        return None
    
    try:
        # Create HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reddit Persona Report - {{ username }}</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }
                .header h1 {
                    color: #667eea;
                    margin: 0;
                    font-size: 2.5em;
                }
                .header p {
                    color: #666;
                    margin: 5px 0;
                }
                .section {
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }
                .section h2 {
                    color: #667eea;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                }
                .trait-list {
                    list-style: none;
                    padding: 0;
                }
                .trait-list li {
                    background: #f8f9fa;
                    margin: 5px 0;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                }
                .interest-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 15px 0;
                }
                .interest-item {
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    border: 1px solid #bbdefb;
                }
                .citation {
                    background: #f5f5f5;
                    border-left: 4px solid #4caf50;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 0 5px 5px 0;
                }
                .citation .quote {
                    font-style: italic;
                    color: #666;
                    margin: 10px 0;
                }
                .metadata {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 30px;
                    text-align: center;
                    font-size: 0.9em;
                    color: #666;
                }
                .confidence-score {
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                }
                .personality-type {
                    font-size: 1.2em;
                    font-weight: bold;
                    color: #667eea;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Reddit Persona Report</h1>
                <p><strong>User:</strong> u/{{ username }}</p>
                <p><strong>Generated:</strong> {{ generated_at }}</p>
                <p><strong>Confidence:</strong> <span class="confidence-score">{{ confidence }}%</span></p>
            </div>
            
            <div class="section">
                <h2>🎭 Personality Profile</h2>
                <p class="personality-type">{{ personality.type }}</p>
                <p>{{ personality.description }}</p>
                
                <h3>Key Traits:</h3>
                <ul class="trait-list">
                    {% for trait in personality.traits %}
                    <li>{{ trait }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <h2>🎯 Interests & Expertise</h2>
                <div class="interest-grid">
                    {% for interest in interests %}
                    <div class="interest-item">
                        <strong>{{ interest }}</strong>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="section">
                <h2>📝 Writing Style</h2>
                <p><strong>Summary:</strong> {{ writing_style.summary }}</p>
                <p><strong>Complexity:</strong> {{ writing_style.complexity }}</p>
                <p><strong>Tone:</strong> {{ writing_style.tone }}</p>
            </div>
            
            {% if social_views %}
            <div class="section">
                <h2>🌍 Social Views</h2>
                <ul class="trait-list">
                    {% for view in social_views %}
                    <li>{{ view }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if citations %}
            <div class="section">
                <h2>📌 Supporting Evidence</h2>
                {% for citation in citations[:5] %}
                <div class="citation">
                    <strong>{{ citation.trait }}</strong><br>
                    <div class="quote">"{{ citation.quote }}"</div>
                    <small>Source: {{ citation.source_type }} in r/{{ citation.subreddit }} (Score: {{ citation.score }})</small>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <div class="metadata">
                <p><strong>Reddit Persona AI</strong> - Intelligent User Analysis Platform</p>
                <p>Crafted by Akshay | Generated with GPT-4 & Advanced NLP</p>
                <p>This report was automatically generated based on public Reddit activity data.</p>
            </div>
        </body>
        </html>
        """
        
        # Prepare data for template
        template_data = {
            'username': persona.get('metadata', {}).get('username', 'Unknown'),
            'generated_at': persona.get('metadata', {}).get('generated_at', datetime.now().isoformat()),
            'confidence': f"{persona.get('metadata', {}).get('confidence_overall', 0) * 100:.1f}",
            'personality': persona.get('personality', {}),
            'interests': persona.get('interests', []),
            'writing_style': persona.get('writing_style', {}),
            'social_views': persona.get('social_views', []),
            'citations': persona.get('citations', [])
        }
        
        # Render template
        template = Template(html_template)
        html_content = template.render(**template_data)
        
        # Generate PDF
        pdf_file = f"{output_dir}/{template_data['username']}_persona_report.pdf"
        
        # Convert HTML to PDF
        weasyprint.HTML(string=html_content).write_pdf(pdf_file)
        
        logger.info(f"PDF report generated: {pdf_file}")
        return pdf_file
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        return None


async def save_json_data(data: Dict[str, Any], filepath: str) -> bool:
    """Save data as JSON file."""
    try:
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info(f"JSON data saved: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON data: {e}")
        return False


async def load_json_data(filepath: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file."""
    try:
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except Exception as e:
        logger.error(f"Error loading JSON data: {e}")
        return None


def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp to readable string."""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unknown"


def calculate_confidence_score(scores: Dict[str, float]) -> float:
    """Calculate overall confidence score from multiple factors."""
    if not scores:
        return 0.0
    
    # Weighted average of confidence factors
    weights = {
        'data_quality': 0.3,
        'analysis_depth': 0.3,
        'citation_count': 0.2,
        'model_confidence': 0.2
    }
    
    total_score = 0.0
    total_weight = 0.0
    
    for factor, weight in weights.items():
        if factor in scores:
            total_score += scores[factor] * weight
            total_weight += weight
    
    return total_score / total_weight if total_weight > 0 else 0.0


def clean_text_for_analysis(text: str) -> str:
    """Clean text for analysis by removing unwanted elements."""
    
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove Reddit formatting
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove markdown links
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\!\?\,\;\:\-\(\)]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text using simple frequency analysis."""
    import re
    from collections import Counter
    
    # Clean text
    text = clean_text_for_analysis(text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Extract words
    words = re.findall(r'\b\w+\b', text)
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency
    word_counts = Counter(words)
    
    # Return top keywords
    return [word for word, count in word_counts.most_common(max_keywords)]


def validate_reddit_username(username: str) -> bool:
    """Validate Reddit username format."""
    import re
    
    # Reddit username rules: 3-20 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))


def extract_reddit_username(input_text: str) -> Optional[str]:
    """
    Extract Reddit username from various input formats.
    
    Args:
        input_text: Input that could be a username, URL, or user link
        
    Returns:
        Clean username or None if invalid
    """
    if not input_text:
        return None
    
    # Remove whitespace
    input_text = input_text.strip()
    
    # Handle different URL formats
    patterns = [
        r'https?://(?:www\.)?reddit\.com/user/([^/?]+)',  # https://reddit.com/user/username
        r'https?://(?:www\.)?reddit\.com/u/([^/?]+)',     # https://reddit.com/u/username
        r'u/([^/?]+)',                                    # u/username
        r'user/([^/?]+)',                                 # user/username
        r'@([^/?]+)',                                     # @username
    ]
    
    for pattern in patterns:
        match = re.search(pattern, input_text, re.IGNORECASE)
        if match:
            username = match.group(1)
            # Remove any trailing slashes or query parameters
            username = username.split('/')[0].split('?')[0]
            return username
    
    # If no URL pattern matches, assume it's already a username
    # Remove any common prefixes if present
    username = input_text
    if username.startswith('u/'):
        username = username[2:]
    elif username.startswith('user/'):
        username = username[5:]
    elif username.startswith('@'):
        username = username[1:]
    
    # Clean up the username
    username = username.split('/')[0].split('?')[0].strip()
    
    # Basic validation - Reddit usernames are 3-20 characters, alphanumeric + underscore + hyphen
    if re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
        return username
    
    return None


def get_file_size_mb(filepath: str) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = Path(filepath).stat().st_size
        return size_bytes / (1024 * 1024)
    except:
        return 0.0


def create_backup(filepath: str) -> str:
    """Create a backup of a file."""
    try:
        path = Path(filepath)
        if not path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.parent / f"{path.stem}_backup_{timestamp}{path.suffix}"
        
        import shutil
        shutil.copy2(path, backup_path)
        
        logger.info(f"Backup created: {backup_path}")
        return str(backup_path)
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None


def cleanup_old_files(directory: str, max_age_days: int = 7):
    """Clean up old files in a directory."""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for file_path in dir_path.iterdir():
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path}")
                    
    except Exception as e:
        logger.error(f"Error cleaning up old files: {e}")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging."""
    import platform
    import psutil
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'disk_usage': psutil.disk_usage('/').percent
    }


def check_dependencies() -> Dict[str, bool]:
    """Check if all required dependencies are available."""
    dependencies = {
        'praw': False,
        'openai': False,
        'plotly': False,
        'fastapi': False,
        'weasyprint': False,
        'nltk': False,
        'sklearn': False
    }
    
    try:
        import praw
        dependencies['praw'] = True
    except ImportError:
        pass
    
    try:
        import openai
        dependencies['openai'] = True
    except ImportError:
        pass
    
    try:
        import plotly
        dependencies['plotly'] = True
    except ImportError:
        pass
    
    try:
        import fastapi
        dependencies['fastapi'] = True
    except ImportError:
        pass
    
    try:
        import weasyprint
        dependencies['weasyprint'] = True
    except ImportError:
        pass
    
    try:
        import nltk
        dependencies['nltk'] = True
    except ImportError:
        pass
    
    try:
        import sklearn
        dependencies['sklearn'] = True
    except ImportError:
        pass
    
    return dependencies


def print_system_status():
    """Print system status and dependency information."""
    print("\n" + "="*50)
    print("🚀 Reddit Persona AI - System Status")
    print("="*50)
    
    # System info
    sys_info = get_system_info()
    print(f"\n💻 System Information:")
    print(f"   Platform: {sys_info['platform']}")
    print(f"   Python: {sys_info['python_version']}")
    print(f"   CPU Cores: {sys_info['cpu_count']}")
    print(f"   Memory: {sys_info['memory_total'] / (1024**3):.1f}GB total")
    print(f"   Disk Usage: {sys_info['disk_usage']:.1f}%")
    
    # Dependencies
    deps = check_dependencies()
    print(f"\n📦 Dependencies:")
    for dep, available in deps.items():
        status = "✅" if available else "❌"
        print(f"   {status} {dep}")
    
    # Environment variables
    print(f"\n🔧 Environment Variables:")
    env_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'OPENAI_API_KEY']
    for var in env_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Not set"
        print(f"   {status} {var}")
    
    print("\n" + "="*50) 