"""
LLM Service Module
Handles API calls to Groq (primary) and Gemini (fallback) for persona generation.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    """Service for handling Groq (primary) and Gemini (fallback) API calls."""

    def __init__(self):
        """Initialize the LLM service with Groq as primary and Gemini as fallback."""
        self.groq_api_key = os.getenv('GROQ_API_KEY', 'your-groq-api-key-here')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
        print(f"[DEBUG] GEMINI_API_KEY used by backend: {self.gemini_api_key[:8]}*********")
        self.groq_client = None
        self.gemini_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize both Groq and Gemini clients."""
        # Initialize Groq client
        try:
            from groq import Groq
            # Simple initialization without any extra parameters
            self.groq_client = Groq(api_key=self.groq_api_key)
            logger.info("Groq client initialized successfully")
        except ImportError:
            logger.warning("Groq library not installed")
            self.groq_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.groq_client = None

        # Initialize Gemini client
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("Gemini client initialized successfully")
        except ImportError:
            logger.warning("Google Generative AI library not installed")
            self.gemini_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.gemini_client = None

    async def generate_persona(self, user_data, analysis_results):
        """Generate a persona using Groq first, then Gemini as fallback."""
        prompt = self._create_persona_prompt(user_data, analysis_results)
        
        # Try Groq first (primary)
        if self.groq_client:
            try:
                response = await self._call_groq_with_retry(prompt)
                return response
            except Exception as e:
                logger.warning(f"Groq API failed, trying Gemini fallback: {e}")
        
        # Try Gemini as fallback
        if self.gemini_client:
            try:
                response = await self._call_gemini_with_retry(prompt)
                return response
            except Exception as e:
                logger.error(f"Gemini API call failed after retries: {e}")
        
        # If both fail, use template
        logger.warning("Both Groq and Gemini failed, using template persona")
        return self._generate_template_persona(user_data, analysis_results)

    async def _call_groq_with_retry(self, prompt: str):
        """Call Groq API with retry logic - optimized for production speed."""
        last_exception = None
        max_retries = 2  # Reduced retries for faster response
        base_delay = 0.5  # Faster retry delays
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.groq_client.chat.completions.create,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    model="llama3-70b-8192",  # Fastest model
                    temperature=0.5,  # Lower temperature for more consistent results
                    max_tokens=3000,  # Reduced for faster response
                    timeout=30  # 30 second timeout
                )
                
                content = response.choices[0].message.content
                persona_data = self._parse_llm_response(content)
                persona_data['metadata']['source'] = 'groq'
                logger.info("Groq API call successful")
                return persona_data
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Groq API attempt {attempt + 1} failed: {e}")
                if "rate" in str(e).lower() or "429" in str(e) or "quota" in str(e).lower():
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Rate limit detected, waiting {delay} seconds before retry")
                    await asyncio.sleep(delay)
                elif attempt < max_retries - 1:
                    await asyncio.sleep(base_delay)
        
        raise last_exception

    async def _call_gemini_with_retry(self, prompt: str):
        """Call Gemini API with retry logic - optimized for production speed."""
        last_exception = None
        max_retries = 2  # Reduced retries for faster response
        base_delay = 0.5  # Faster retry delays
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.gemini_client.generate_content,
                    prompt,
                    generation_config={
                        'temperature': 0.5,
                        'max_output_tokens': 3000,
                        'top_p': 0.8,
                        'top_k': 40
                    }
                )
                content = response.text
                persona_data = self._parse_llm_response(content)
                persona_data['metadata']['source'] = 'gemini'
                logger.info("Gemini API call successful")
                return persona_data
            except Exception as e:
                last_exception = e
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {e}")
                if "rate" in str(e).lower() or "429" in str(e) or "quota" in str(e).lower():
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Rate limit detected, waiting {delay} seconds before retry")
                    await asyncio.sleep(delay)
                elif attempt < max_retries - 1:
                    await asyncio.sleep(base_delay)
        raise last_exception

    def _create_persona_prompt(self, user_data, analysis_results):
        """Create a prompt for enhanced persona generation in Lucas Mellor format."""
        
        # Extract key information
        username = user_data.get('username', 'Unknown')
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        user_info = user_data.get('user_info', {})
        
        # Format sample posts and comments for context
        sample_posts_text = ""
        if posts:
            sample_posts_text = "\nSample Posts:\n"
            for i, post in enumerate(posts[:5], 1):
                sample_posts_text += f"{i}. Title: {post.get('title', 'No title')}\n"
                sample_posts_text += f"   Subreddit: r/{post.get('subreddit', 'unknown')}\n"
                sample_posts_text += f"   Score: {post.get('score', 0)} | Comments: {post.get('num_comments', 0)}\n"
                if post.get('body'):
                    sample_posts_text += f"   Content: {post.get('body', '')[:200]}...\n"
                sample_posts_text += f"   URL: {post.get('permalink', '')}\n\n"
        
        sample_comments_text = ""
        if comments:
            sample_comments_text = "\nSample Comments:\n"
            for i, comment in enumerate(comments[:5], 1):
                sample_comments_text += f"{i}. Subreddit: r/{comment.get('subreddit', 'unknown')}\n"
                sample_comments_text += f"   Score: {comment.get('score', 0)}\n"
                sample_comments_text += f"   Content: {comment.get('body', '')[:200]}...\n"
                sample_comments_text += f"   URL: {comment.get('permalink', '')}\n\n"
        
        # Create analysis summary
        analysis_summary = f"""
User Analysis Summary:
- Username: u/{username}
- Account Age: {self._format_account_age(user_info.get('created_utc'))}
- Karma: {user_info.get('link_karma', 0)} post, {user_info.get('comment_karma', 0)} comment
- Total Posts: {len(posts)}
- Total Comments: {len(comments)}
- Analysis Score: {analysis_results.get('confidence_score', 75)}

Analysis Results:
- Sentiment: {analysis_results.get('sentiment_analysis', {}).get('overall_sentiment', 'neutral')}
- Personality Type: {analysis_results.get('personality_traits', {}).get('personality_type', 'Unknown')}
- Key Interests: {', '.join([interest[0] for interest in analysis_results.get('interests', {}).get('top_interests', [])[:5]])}
- Writing Style: {analysis_results.get('writing_style', {}).get('summary', 'Standard')}
- Activity Level: {analysis_results.get('activity_patterns', {}).get('activity_pattern', 'Moderate')}
"""
        
        prompt = f"""
You are an expert user researcher and psychologist specializing in creating detailed user personas based on Reddit activity data. Create a comprehensive persona in the EXACT format of the Lucas Mellor example, including real post and comment data.

{analysis_summary}

{sample_posts_text}

{sample_comments_text}

Generate a detailed persona with this EXACT JSON structure (matching Lucas Mellor format):

{{
    "name": "{username}",
    "age": 25-65 (estimate based on content maturity and interests),
    "occupation": "Job title based on content and expertise shown",
    "status": "Single/Married/In Relationship (if mentioned)",
    "location": "City, Country (if mentioned in posts/comments)",
    "tier": "Reddit User/Early Adopter/Influencer/Expert",
    "archetype": "The Creator/The Explorer/The Helper/The Achiever/The Individualist/The Caregiver/The Enthusiast/The Challenger/The Peacemaker",
    "traits": ["trait1", "trait2", "trait3", "trait4"],
    "motivations": {{
        "convenience": 0-100,
        "wellness": 0-100,
        "speed": 0-100,
        "preferences": 0-100,
        "comfort": 0-100,
        "dietary_needs": 0-100
    }},
    "personality": {{
        "introvert": 0-100,
        "extrovert": 0-100,
        "intuition": 0-100,
        "sensing": 0-100,
        "feeling": 0-100,
        "thinking": 0-100,
        "perceiving": 0-100,
        "judging": 0-100
    }},
    "behavior_habits": [
        "Specific behavior based on their Reddit activity",
        "Another specific behavior pattern",
        "Third behavior pattern"
    ],
    "frustrations": [
        "Frustration inferred from their posts/comments",
        "Another frustration they express",
        "Third frustration pattern"
    ],
    "goals_needs": [
        "Goal or need expressed in their content",
        "Another goal or need",
        "Third goal or need"
    ],
    "quote": "A representative 20+ word quote from their actual posts or comments",
    "reddit_username": "u/{username}",
    "analysis_score": 75-95,
    "real_posts": [
        {{
            "title": "Actual post title",
            "subreddit": "r/subreddit_name",
            "score": 123,
            "content": "First 100 characters of post content...",
            "url": "https://reddit.com/permalink"
        }}
    ],
    "real_comments": [
        {{
            "subreddit": "r/subreddit_name",
            "score": 45,
            "content": "First 100 characters of comment content...",
            "url": "https://reddit.com/permalink"
        }}
    ],
    "interests": ["interest1", "interest2", "interest3"],
    "writing_style": {{
        "summary": "Writing style description",
        "complexity": "Simple/Moderate/Complex",
        "tone": "Formal/Casual/Humorous/Analytical/etc"
    }},
    "social_views": ["view1", "view2"],
    "activity_patterns": {{
        "frequency": "Daily/Weekly/etc",
        "peak_hours": "When they're most active",
        "engagement_style": "How they interact"
    }}
}}

CRITICAL REQUIREMENTS:
1. Use the Reddit username "{username}" as the persona name - do NOT generate fictional names
2. Use ONLY real data from their actual posts and comments
3. The quote must be a real quote from their content (20+ words)
4. Include 2-3 real posts and 2-3 real comments in the data
5. All insights must be backed by their actual Reddit activity
6. Motivation scores should reflect their priorities based on content
7. Personality scores should be MBTI-style spectrum (0-100 each dimension)
8. Behavior habits, frustrations, and goals must be inferred from their actual posts/comments
9. Make the persona realistic and data-driven
10. If information is not available, use reasonable defaults but mark analysis_score lower

Base everything on the actual Reddit data provided. The persona should look like a real user profile with genuine insights from their online behavior.
"""
        
        return prompt
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response and extract JSON."""
        import re
        try:
            # Try to extract JSON from the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                # Remove trailing commas before closing braces
                json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
                # Remove newlines and fix quotes
                json_str = json_str.replace('\\n', ' ').replace('\\"', '"')
                persona_data = json.loads(json_str)
                if 'metadata' not in persona_data:
                    persona_data['metadata'] = {}
                persona_data['metadata']['generated_at'] = self._get_current_timestamp()
                persona_data['formatted_text'] = self._format_persona_text_with_citations(persona_data)
                return persona_data
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            # Fallback to template persona
            return self._generate_template_persona(None, None) # Pass dummy values to avoid errors
    
    def _format_persona_text(self, persona_data: Dict[str, Any]) -> str:
        """Format persona data as readable text."""
        username = persona_data.get('username', 'Unknown')
        personality = persona_data.get('personality', {})
        interests = persona_data.get('interests', [])
        writing_style = persona_data.get('writing_style', {})
        social_views = persona_data.get('social_views', [])
        activity_patterns = persona_data.get('activity_patterns', {})
        confidence_score = persona_data.get('confidence_score', 0.0)
        citations = persona_data.get('citations', [])
        
        text = f"""
🚀 REDDIT PERSONA REPORT
{'='*50}

👤 USER: u/{username}
📊 CONFIDENCE: {confidence_score:.1%}
⏰ GENERATED: {self._get_current_timestamp()}

🎭 PERSONALITY PROFILE
{'-'*30}
Type: {personality.get('type', 'Unknown')}
Description: {personality.get('description', 'No description available')}

Key Traits:
{chr(10).join([f"• {trait}" for trait in personality.get('traits', [])])}

🎯 INTERESTS & EXPERTISE
{'-'*30}
{chr(10).join([f"• {interest}" for interest in interests])}

📝 WRITING STYLE
{'-'*30}
Summary: {writing_style.get('summary', 'No analysis available')}
Complexity: {writing_style.get('complexity', 'Unknown')}
Tone: {writing_style.get('tone', 'Unknown')}

🌍 SOCIAL VIEWS
{'-'*30}
{chr(10).join([f"• {view}" for view in social_views])}

📈 ACTIVITY PATTERNS
{'-'*30}
Frequency: {activity_patterns.get('frequency', 'Unknown')}
Peak Hours: {activity_patterns.get('peak_hours', 'Unknown')}
Engagement Style: {activity_patterns.get('engagement_style', 'Unknown')}

📌 SUPPORTING EVIDENCE
{'-'*30}
"""
        
        for i, citation in enumerate(citations[:5], 1):
            text += f"""
{i}. {citation.get('trait', 'Unknown Trait')}
   Quote: "{citation.get('quote', 'No quote')}"
   Source: {citation.get('source_type', 'Unknown')} in r/{citation.get('subreddit', 'Unknown')}
   Score: {citation.get('score', 0)}
"""
        
        text += f"""
{'='*50}
🤖 Generated by PersonaForge AI
📊 Powered by Advanced NLP & LLM Analysis
"""
        
        return text

    def _format_persona_text_with_citations(self, persona_data: dict) -> str:
        """Generate formatted text with citations for each characteristic."""
        username = persona_data.get('name', persona_data.get('reddit_username', 'Unknown'))
        confidence = persona_data.get('metadata', {}).get('confidence_overall', 0.0) * 100
        generated_at = persona_data.get('metadata', {}).get('generated_at', 'Unknown')
        
        text = f"""
🚀 REDDIT PERSONA REPORT
==================================================

👤 USER: u/{username}
📊 CONFIDENCE: {confidence:.1f}%
⏰ GENERATED: {generated_at}

🎭 PERSONALITY PROFILE
------------------------------"""
        
        # Personality type
        personality_type = "Unknown"
        if 'personality_type' in persona_data:
            personality_type = persona_data['personality_type']
        elif 'personality' in persona_data and 'mbti_type' in persona_data['personality']:
            personality_type = persona_data['personality']['mbti_type']
        elif 'personality' in persona_data and 'type' in persona_data['personality']:
            personality_type = persona_data['personality']['type']
        
        text += f"""
Type: {personality_type}
Description: {persona_data.get('archetype', 'Active Reddit user')}

Key Traits:"""
        
        # Traits with citations
        traits = persona_data.get('traits', [])
        for trait in traits:
            text += f"\n• {trait}"
        
        text += f"""

🎯 INTERESTS & EXPERTISE
------------------------------"""
        
        # Interests with citations
        interests = persona_data.get('interests', [])
        for interest in interests:
            text += f"\n• {interest}"
        
        text += f"""

📝 WRITING STYLE
------------------------------
Summary: {persona_data.get('writing_style', {}).get('summary', 'Not available')}
Complexity: {persona_data.get('writing_style', {}).get('complexity', 'Not available')}
Tone: {persona_data.get('writing_style', {}).get('tone', 'Not available')}

🌍 SOCIAL VIEWS
------------------------------"""
        
        # Social views with citations
        social_views = persona_data.get('social_views', [])
        for view in social_views:
            text += f"\n• {view}"
        
        text += f"""

📈 ACTIVITY PATTERNS
------------------------------
Frequency: {persona_data.get('activity_patterns', {}).get('frequency', 'Not available')}
Peak Hours: {persona_data.get('activity_patterns', {}).get('peak_hours', 'Not available')}
Engagement Style: {persona_data.get('activity_patterns', {}).get('engagement_style', 'Not available')}

🎯 MOTIVATIONS
------------------------------"""
        
        # Motivations with scores
        motivations = persona_data.get('motivations', {})
        for motivation, score in motivations.items():
            text += f"\n• {motivation.replace('_', ' ').title()}: {score}/100"
        
        text += f"""

💭 BEHAVIOR HABITS
------------------------------"""
        
        # Behavior habits with citations
        habits = persona_data.get('behavior_habits', [])
        for habit in habits:
            text += f"\n• {habit}"
        
        text += f"""

😤 FRUSTRATIONS
------------------------------"""
        
        # Frustrations with citations
        frustrations = persona_data.get('frustrations', [])
        for frustration in frustrations:
            text += f"\n• {frustration}"
        
        text += f"""

🎯 GOALS & NEEDS
------------------------------"""
        
        # Goals with citations
        goals = persona_data.get('goals_needs', [])
        for goal in goals:
            text += f"\n• {goal}"
        
        text += f"""

💬 REPRESENTATIVE QUOTE
------------------------------
"{persona_data.get('quote', 'No representative quote available')}"

📌 SUPPORTING EVIDENCE
------------------------------"""
        
        # Real posts with citations
        real_posts = persona_data.get('real_posts', [])
        if real_posts:
            text += f"\n📝 KEY POSTS ({len(real_posts)} analyzed):"
            for i, post in enumerate(real_posts[:3], 1):
                title = post.get('title', 'No title')
                subreddit = post.get('subreddit', 'Unknown')
                score = post.get('score', 0)
                text += f"\n{i}. \"{title}\" (r/{subreddit}, {score} points)"
                text += f"\n   URL: {post.get('url', 'No URL')}"
        
        # Real comments with citations
        real_comments = persona_data.get('real_comments', [])
        if real_comments:
            text += f"\n\n💬 KEY COMMENTS ({len(real_comments)} analyzed):"
            for i, comment in enumerate(real_comments[:3], 1):
                content = comment.get('content', 'No content')[:100] + "..." if len(comment.get('content', '')) > 100 else comment.get('content', 'No content')
                subreddit = comment.get('subreddit', 'Unknown')
                score = comment.get('score', 0)
                text += f"\n{i}. \"{content}\" (r/{subreddit}, {score} points)"
                text += f"\n   URL: {comment.get('url', 'No URL')}"
        
        # Analysis metadata
        analysis_score = persona_data.get('analysis_score', 0)
        source = persona_data.get('metadata', {}).get('source', 'Unknown')
        text += f"""

📊 ANALYSIS METADATA
------------------------------
Analysis Score: {analysis_score}/100
Data Source: {source}
Total Posts Analyzed: {len(real_posts)}
Total Comments Analyzed: {len(real_comments)}

==================================================
🤖 Generated by PersonaForge AI
📊 Powered by Advanced NLP & LLM Analysis
🔗 Each characteristic is backed by actual Reddit activity data
"""
        
        return text.strip()
    
    def _generate_template_persona(self, user_data, analysis_results):
        """Generate a template-based persona when LLM is not available."""
        username = user_data.get('username', 'Unknown')
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        
        # Extract sample posts and comments for template
        sample_posts = []
        sample_comments = []
        
        if posts:
            for post in posts[:3]:
                sample_posts.append({
                    'title': post.get('title', 'No title'),
                    'subreddit': post.get('subreddit', 'unknown'),
                    'score': post.get('score', 0),
                    'content': post.get('body', '')[:100] + '...' if post.get('body') else '',
                    'url': f"https://reddit.com{post.get('permalink', '')}"
                })
        
        if comments:
            for comment in comments[:3]:
                sample_comments.append({
                    'subreddit': comment.get('subreddit', 'unknown'),
                    'score': comment.get('score', 0),
                    'content': comment.get('body', '')[:100] + '...' if comment.get('body') else '',
                    'url': f"https://reddit.com{comment.get('permalink', '')}"
                })
        
        # Generate a representative quote
        quote = "I enjoy participating in online discussions and sharing my thoughts with the community."
        if posts and posts[0].get('body'):
            quote = posts[0].get('body', '')[:50] + '...'
        elif comments and comments[0].get('body'):
            quote = comments[0].get('body', '')[:50] + '...'
        
        persona_data = {
            "name": username,
            "age": 28,
            "occupation": "Online Community Member",
            "status": "Active",
            "location": "Internet",
            "tier": "Reddit User",
            "archetype": "The Explorer",
            "traits": ["Engaged", "Opinionated", "Community-focused", "Active"],
            "motivations": {
                "convenience": 75,
                "wellness": 60,
                "speed": 70,
                "preferences": 80,
                "comfort": 65,
                "dietary_needs": 50
            },
            "personality": {
                "introvert": 40,
                "extrovert": 60,
                "intuition": 55,
                "sensing": 45,
                "feeling": 50,
                "thinking": 50,
                "perceiving": 45,
                "judging": 55
            },
            "behavior_habits": [
                "Regularly participates in online discussions",
                "Shares opinions and experiences with the community",
                "Engages with content across multiple subreddits"
            ],
            "frustrations": [
                "Limited information in some posts",
                "Difficulty finding relevant content",
                "Inconsistent community responses"
            ],
            "goals_needs": [
                "To connect with like-minded individuals",
                "To share knowledge and experiences",
                "To stay informed about topics of interest"
            ],
            "quote": quote,
            "reddit_username": f"u/{username}",
            "analysis_score": 65,
            "real_posts": sample_posts,
            "real_comments": sample_comments,
            "interests": ["Community Discussion", "Information Sharing", "Online Engagement"],
            "writing_style": {
                "summary": "Clear and communicative",
                "complexity": "Moderate",
                "tone": "Engaging"
            },
            "social_views": ["Community-oriented", "Information sharing"],
            "activity_patterns": {
                "frequency": "Regular",
                "peak_hours": "Evening",
                "engagement_style": "Active participant"
            },
            "metadata": {
                "source": "template",
                "generated_at": self._get_current_timestamp(),
                "username": username,
                "confidence_overall": 0.3
            },
            "formatted_text": f"""
🚀 REDDIT PERSONA REPORT
{'='*50}

👤 USER: u/{username}
📊 CONFIDENCE: 30.0%
⏰ GENERATED: {self._get_current_timestamp()}

🎭 PERSONALITY PROFILE
{'-'*30}
Type: ENFP (Template)
Description: An active Reddit user who enjoys participating in online communities and sharing thoughts with others.

Key Traits:
• Engaged
• Opinionated
• Community-focused
• Active

🎯 INTERESTS & EXPERTISE
{'-'*30}
• Community Discussion
• Information Sharing
• Online Engagement

📝 WRITING STYLE
{'-'*30}
Summary: Clear and communicative
Complexity: Moderate
Tone: Engaging

🌍 SOCIAL VIEWS
{'-'*30}
• Community-oriented
• Information sharing

📈 ACTIVITY PATTERNS
{'-'*30}
Frequency: Regular
Peak Hours: Evening
Engagement Style: Active participant

📌 SUPPORTING EVIDENCE
{'-'*30}
Template-based analysis - limited real data available

{'='*50}
🤖 Generated by PersonaForge AI
📊 Powered by Advanced NLP & LLM Analysis
"""
        }
        
        return persona_data
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _format_account_age(self, created_utc: Optional[float]) -> str:
        """Format account age from Unix timestamp."""
        if not created_utc:
            return "Unknown"
        
        try:
            from datetime import datetime
            created_date = datetime.fromtimestamp(created_utc)
            current_date = datetime.now()
            age_delta = current_date - created_date
            
            years = age_delta.days // 365
            months = (age_delta.days % 365) // 30
            
            if years > 0:
                return f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''}"
            else:
                return f"{months} month{'s' if months != 1 else ''}"
        except Exception:
            return "Unknown"
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of LLM providers."""
        return {
            "groq_available": self.groq_client is not None,
            "gemini_available": self.gemini_client is not None,
            "primary_provider": "groq",
            "fallback_provider": "gemini",
            "confidence_overall": 0.9 if self.groq_client else (0.7 if self.gemini_client else 0.1)
        } 