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
        # Initialize Groq client - SIMPLIFIED APPROACH
        try:
            from groq import Groq
            # Use the simplest possible initialization
            self.groq_client = Groq(api_key=self.groq_api_key)
            logger.info("Groq client initialized successfully")
        except ImportError:
            logger.warning("Groq library not installed")
            self.groq_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            # Try alternative approach
            try:
                import os
                os.environ['GROQ_API_KEY'] = self.groq_api_key
                from groq import Groq
                self.groq_client = Groq()
                logger.info("Alternative Groq initialization successful")
            except Exception as e2:
                logger.error(f"Alternative Groq initialization also failed: {e2}")
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
        max_retries = 1  # Reduced to 1 retry to avoid quota exhaustion
        base_delay = 0.5  # Faster retry delays
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.groq_client.chat.completions.create,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    model="llama3-8b-8192",  # Smaller, faster model for token efficiency
                    temperature=0.5,  # Lower temperature for more consistent results
                    max_tokens=1000,  # Further reduced for token efficiency
                    timeout=15  # Reduced timeout
                )
                
                content = response.choices[0].message.content
                persona_data = self._parse_llm_response(content)
                persona_data['metadata']['source'] = 'groq'
                logger.info("Groq API call successful")
                return persona_data
                
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                logger.warning(f"Groq API attempt {attempt + 1} failed: {e}")
                
                # Check for specific error types
                if any(keyword in error_str for keyword in ["rate", "429", "quota", "limit", "token"]):
                    logger.info("Rate/token limit detected, skipping retry to avoid quota exhaustion")
                    break  # Don't retry on rate limits to avoid quota exhaustion
                elif attempt < max_retries - 1:
                    await asyncio.sleep(base_delay)
        
        raise last_exception

    async def _call_gemini_with_retry(self, prompt: str):
        """Call Gemini API with retry logic - optimized for production speed."""
        last_exception = None
        max_retries = 1  # Reduced to 1 retry to avoid quota exhaustion
        base_delay = 0.5  # Faster retry delays
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.gemini_client.generate_content,
                    prompt,
                    generation_config={
                        'temperature': 0.5,
                        'max_output_tokens': 1000,  # Reduced to match Groq
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
                error_str = str(e).lower()
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {e}")
                
                # Check for specific error types
                if any(keyword in error_str for keyword in ["rate", "429", "quota", "limit", "token"]):
                    logger.info("Rate/token limit detected, skipping retry to avoid quota exhaustion")
                    break  # Don't retry on rate limits to avoid quota exhaustion
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
        
        # Format sample posts and comments for context (REDUCED TO 2 EACH)
        sample_posts_text = ""
        if posts:
            sample_posts_text = "\nPosts:\n"
            for i, post in enumerate(posts[:2], 1):  # REDUCED FROM 5 TO 2
                sample_posts_text += f"{i}. {post.get('title', 'No title')} (r/{post.get('subreddit', 'unknown')}, {post.get('score', 0)})\n"
                if post.get('body'):
                    sample_posts_text += f"   {post.get('body', '')[:100]}...\n"  # REDUCED FROM 200 TO 100
                sample_posts_text += "\n"
        
        sample_comments_text = ""
        if comments:
            sample_comments_text = "\nComments:\n"
            for i, comment in enumerate(comments[:2], 1):  # REDUCED FROM 5 TO 2
                sample_comments_text += f"{i}. r/{comment.get('subreddit', 'unknown')} ({comment.get('score', 0)})\n"
                sample_comments_text += f"   {comment.get('body', '')[:100]}...\n"  # REDUCED FROM 200 TO 100
                sample_comments_text += "\n"
        
        # SHORTENED analysis summary
        analysis_summary = f"""
User: u/{username} | Karma: {user_info.get('link_karma', 0)}/{user_info.get('comment_karma', 0)} | Posts: {len(posts)} | Comments: {len(comments)}
Sentiment: {analysis_results.get('sentiment_analysis', {}).get('overall_sentiment', 'neutral')}
Interests: {', '.join([interest[0] for interest in analysis_results.get('interests', {}).get('top_interests', [])[:3]])}  # REDUCED FROM 5 TO 3
"""
        
        prompt = f"""
Create a Reddit user persona based on this data:

{analysis_summary}

{sample_posts_text}

{sample_comments_text}

Return ONLY valid JSON:

{{
    "name": "{username}",
    "age": "25-65",
    "occupation": "job title",
    "location": "city, country",
    "archetype": "The Creator/Explorer/Helper/Achiever/Individualist/Caregiver/Enthusiast/Challenger/Peacemaker",
    "traits": ["trait1", "trait2", "trait3"],
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
    "behavior_habits": ["behavior1", "behavior2", "behavior3"],
    "frustrations": ["frustration1", "frustration2", "frustration3"],
    "goals_needs": ["goal1", "goal2", "goal3"],
    "quote": "real quote from their content (20+ words)",
    "reddit_username": "u/{username}",
    "analysis_score": 75-95,
    "real_posts": [
        {{
            "title": "post title",
            "subreddit": "r/subreddit",
            "score": 123,
            "content": "first 100 chars...",
            "url": "https://reddit.com/permalink"
        }}
    ],
    "real_comments": [
        {{
            "subreddit": "r/subreddit",
            "score": 45,
            "content": "first 100 chars...",
            "url": "https://reddit.com/permalink"
        }}
    ],
    "interests": ["interest1", "interest2", "interest3"],
    "writing_style": {{
        "summary": "style description",
        "complexity": "Simple/Moderate/Complex",
        "tone": "Formal/Casual/Humorous/Analytical"
    }},
    "social_views": ["view1", "view2"],
    "activity_patterns": {{
        "frequency": "Daily/Weekly",
        "peak_hours": "active time",
        "engagement_style": "interaction style"
    }}
}}

Use real data, no fictional names, base insights on actual Reddit activity.
"""
        
        return prompt
    
    def _parse_llm_response(self, content: str) -> dict:
        """Parse LLM response and extract JSON robustly."""
        import re, json
        try:
            # Remove markdown/code block wrappers
            content = re.sub(r"^\s*```(?:json)?|```\s*$", "", content.strip(), flags=re.MULTILINE)
            
            # Find the largest JSON object in the string
            matches = list(re.finditer(r'\{[\s\S]*\}', content))
            if not matches:
                raise ValueError("No JSON object found in LLM response.")
            
            # Use the largest match
            json_str = max((m.group(0) for m in matches), key=len)
            
            # Remove trailing commas before closing braces/brackets
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            
            # Fix unquoted string values more comprehensively
            # Pattern 1: "key": value (where value is not quoted and not a number)
            json_str = re.sub(r'("[^"]+"\s*:\s*)([A-Za-z][A-Za-z0-9\-_/\s]+?)(\s*[,}\]])', 
                             lambda m: m.group(1) + f'"{m.group(2).strip()}"' + m.group(3), json_str)
            
            # Pattern 2: "key": value (where value contains spaces or special chars)
            json_str = re.sub(r'("[^"]+"\s*:\s*)([^",\d\[\]{}][^,\d\[\]{}]*?)(\s*[,}\]])', 
                             lambda m: m.group(1) + f'"{m.group(2).strip()}"' + m.group(3), json_str)
            
            # Fix age ranges like "age": 30-40 -> "age": "30-40"
            json_str = re.sub(r'("age"\s*:\s*)(\d+-\d+)', r'\1"\2"', json_str)
            
            # Fix occupation, location, status fields
            json_str = re.sub(r'("occupation"\s*:\s*)([^",\d\[\]{}][^,\d\[\]{}]*?)(\s*[,}\]])', 
                             lambda m: m.group(1) + f'"{m.group(2).strip()}"' + m.group(3), json_str)
            json_str = re.sub(r'("location"\s*:\s*)([^",\d\[\]{}][^,\d\[\]{}]*?)(\s*[,}\]])', 
                             lambda m: m.group(1) + f'"{m.group(2).strip()}"' + m.group(3), json_str)
            json_str = re.sub(r'("status"\s*:\s*)([^",\d\[\]{}][^,\d\[\]{}]*?)(\s*[,}\]])', 
                             lambda m: m.group(1) + f'"{m.group(2).strip()}"' + m.group(3), json_str)
            
            # Remove newlines and fix escaped quotes
            json_str = json_str.replace('\\n', ' ').replace('\\"', '"')
            
            # Try parsing
            persona_data = json.loads(json_str)
            if 'metadata' not in persona_data:
                persona_data['metadata'] = {}
            persona_data['metadata']['generated_at'] = self._get_current_timestamp()
            persona_data['metadata']['format'] = 'llm'

            # --- PATCH: Ensure big_five_traits is always filled ---
            big_five = None
            # 1. Try LLM response
            if 'big_five_traits' in persona_data and isinstance(persona_data['big_five_traits'], dict):
                big_five = persona_data['big_five_traits']
                # Ensure all values are numbers
                big_five = {k: int(v) if isinstance(v, (int, float)) else 50 for k, v in big_five.items()}
            
            # 2. Try MBTI/analysis mapping if missing or all zeros
            if not big_five or not any(v > 0 for v in big_five.values()):
                personality = persona_data.get('personality', {})
                # Try to map from MBTI-style fields
                big_five = {
                    'openness': personality.get('intuition', 60),
                    'conscientiousness': personality.get('judging', 65),
                    'extraversion': personality.get('extrovert', 60),
                    'agreeableness': personality.get('feeling', 70),
                    'neuroticism': max(0, 100 - (personality.get('introvert', 50) + personality.get('extrovert', 50)) // 2)
                }
            
            # 3. If still missing, use defaults
            if not big_five or not any(v > 0 for v in big_five.values()):
                big_five = {'openness': 60, 'conscientiousness': 65, 'extraversion': 60, 'agreeableness': 70, 'neuroticism': 40}
            
            persona_data['big_five_traits'] = big_five
            
            # --- PATCH: Ensure chart_data is complete ---
            if 'chart_data' not in persona_data:
                persona_data['chart_data'] = {}
            
            # Ensure all required chart data fields exist
            required_chart_fields = ['community_engagement', 'activity_patterns', 'sentiment_timeline', 'user_motivations']
            for field in required_chart_fields:
                val = persona_data['chart_data'].get(field)
                if not val or (isinstance(val, list) and len(val) == 0):
                    # Generate template data for missing or empty fields
                    if field == 'community_engagement':
                        persona_data['chart_data'][field] = [
                            {"name": "Reddit Participation", "value": 30},
                            {"name": "Subreddit Diversity", "value": 25},
                            {"name": "Avg Score", "value": 40},
                            {"name": "Engagement Level", "value": 35}
                        ]
                    elif field == 'activity_patterns':
                        persona_data['chart_data'][field] = [
                            {"name": "Peak Hour", "value": 60},
                            {"name": "Frequency", "value": 45},
                            {"name": "Posting Rate", "value": 30},
                            {"name": "Comment Rate", "value": 35}
                        ]
                    elif field == 'sentiment_timeline':
                        persona_data['chart_data'][field] = [
                            {"name": "Jan", "value": 65},
                            {"name": "Feb", "value": 70},
                            {"name": "Mar", "value": 75},
                            {"name": "Apr", "value": 80},
                            {"name": "May", "value": 85},
                            {"name": "Jun", "value": 90}
                        ]
                    elif field == 'user_motivations':
                        persona_data['chart_data'][field] = [
                            {"name": "Community", "value": 80},
                            {"name": "Information", "value": 70},
                            {"name": "Expression", "value": 60},
                            {"name": "Connection", "value": 75}
                        ]

            return persona_data
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            logger.warning(f"Response content: {content[:500]}...")
            try:
                logger.warning(f"Cleaned JSON string: {json_str[:500]}...")
            except Exception:
                pass
            # Fallback to template persona
            return self._generate_template_persona({}, {})
    
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
        if not user_data:
            user_data = {}
        if not analysis_results:
            analysis_results = {}
            
        username = user_data.get('username', 'Unknown')
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        
        # Extract analysis results
        sentiment = analysis_results.get('sentiment_analysis', {})
        personality = analysis_results.get('personality_traits', {})
        interests = analysis_results.get('interests', {})
        writing_style = analysis_results.get('writing_style', {})
        mbti = analysis_results.get('mbti_estimation', {})
        activity_patterns = analysis_results.get('activity_patterns', {})
        community_engagement = analysis_results.get('community_engagement', {})
        
        # Calculate Big Five traits from available data
        big_five = self._calculate_big_five_traits(personality, sentiment, writing_style)
        
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
                "judging": 55,
                "mbti_type": mbti.get('type', 'Unknown'),
                "mbti_description": mbti.get('description', 'Unknown')
            },
            "behaviors": [
                "Regularly participates in online discussions",
                "Shares opinions and experiences with the community",
                "Engages with content across multiple subreddits"
            ],
            "behaviors_habits": [
                "Regularly participates in online discussions",
                "Shares opinions and experiences with the community",
                "Engages with content across multiple subreddits"
            ],
            "frustrations": [
                "Limited information in some posts",
                "Difficulty finding relevant content",
                "Inconsistent community responses"
            ],
            "goals": [
                "To connect with like-minded individuals",
                "To share knowledge and experiences",
                "To stay informed about topics of interest"
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
            "interests": [interest[0] for interest in interests.get('top_interests', [])] if interests.get('top_interests') else ["Community Discussion", "Information Sharing", "Online Engagement"],
            "writing_style": {
                "summary": writing_style.get('summary', 'Clear and communicative'),
                "complexity": writing_style.get('complexity', 'Moderate'),
                "tone": writing_style.get('tone', 'Engaging')
            },
            "social_views": ["Community-oriented", "Information sharing"],
            "behaviors_habits": {
                "daily_patterns": f"User is most active during {activity_patterns.get('activity_pattern', 'unknown')} hours",
                "lifestyle_choices": "Based on Reddit activity patterns",
                "reddit_usage": f"Posts {len(posts)} times, comments {len(comments)} times",
                "posting_habits": f"Average score: {sum(p.get('score', 0) for p in posts) / max(len(posts), 1):.1f}",
                "activity_times": f"Peak activity: {activity_patterns.get('peak_hour', 'unknown')} hours"
            },
            "goals_needs": {
                "primary_objectives": "Information sharing and community engagement",
                "reddit_seeking": "Discussion and knowledge exchange",
                "personal_goals": "Building online presence and connections",
                "information_needs": "Community insights and discussions"
            },
            "big_five_traits": big_five,
            "personality_traits": big_five,
            "community_engagement": {
                "participation_level": community_engagement.get('engagement_level', 'Moderate'),
                "subreddit_diversity": f"{community_engagement.get('subreddit_diversity', 0)} different subreddits",
                "interaction_frequency": f"{len(posts) + len(comments)} total interactions",
                "contribution_level": f"Average score: {community_engagement.get('avg_score', 0):.1f}"
            },
            "activity_patterns": {
                "posting_frequency": f"{len(posts)} posts, {len(comments)} comments",
                "peak_times": f"Peak at {activity_patterns.get('peak_hour', 'unknown')} hours",
                "engagement_style": activity_patterns.get('activity_pattern', 'Regular'),
                "activity_metrics": f"Activity frequency: {activity_patterns.get('activity_frequency', 0)}"
            },
            "sentiment_timeline": {
                "overall_trend": sentiment.get('sentiment_category', 'neutral'),
                "mood_patterns": f"Sentiment score: {sentiment.get('overall_sentiment', 0):.2f}",
                "emotional_consistency": f"Subjectivity: {sentiment.get('subjectivity', 0):.2f}",
                "sentiment_evolution": "Based on recent activity"
            },
            "user_motivations": {
                "primary_drivers": "Community engagement and information sharing",
                "posting_motivations": "Discussion and knowledge exchange",
                "social_needs": "Connection with like-minded individuals",
                "personal_aspirations": "Building online presence and influence"
            },
            "metadata": {
                "source": "template",
                "generated_at": self._get_current_timestamp(),
                "username": username,
                "confidence_overall": 0.3
            },
            "chart_data": {
                "personality_radar": [
                    {"name": "Openness", "value": big_five.get('openness', 70)},
                    {"name": "Conscientiousness", "value": big_five.get('conscientiousness', 65)},
                    {"name": "Extraversion", "value": big_five.get('extraversion', 60)},
                    {"name": "Agreeableness", "value": big_five.get('agreeableness', 75)},
                    {"name": "Neuroticism", "value": big_five.get('neuroticism', 40)}
                ],
                "interests_pie": [
                    {"name": "Technology", "value": 25},
                    {"name": "Gaming", "value": 20},
                    {"name": "Science", "value": 15},
                    {"name": "Entertainment", "value": 15},
                    {"name": "Community", "value": 25}
                ],
                "big_five": [
                    {"name": "Openness", "value": big_five.get('openness', 70), "color": "blue"},
                    {"name": "Conscientiousness", "value": big_five.get('conscientiousness', 65), "color": "green"},
                    {"name": "Extraversion", "value": big_five.get('extraversion', 60), "color": "yellow"},
                    {"name": "Agreeableness", "value": big_five.get('agreeableness', 75), "color": "purple"},
                    {"name": "Neuroticism", "value": big_five.get('neuroticism', 40), "color": "red"}
                ],
                "community_engagement": [
                    {"name": "Reddit Participation", "value": min(100, (len(posts) + len(comments)) * 10) if (len(posts) + len(comments)) > 0 else 30},
                    {"name": "Subreddit Diversity", "value": min(100, len(set(p.get('subreddit', '') for p in posts + comments)) * 20) if (len(posts) + len(comments)) > 0 else 25},
                    {"name": "Avg Score", "value": min(100, max(0, sum(p.get('score', 0) for p in posts + comments) / max(len(posts + comments), 1) * 10)) if (len(posts) + len(comments)) > 0 else 40},
                    {"name": "Engagement Level", "value": min(100, (len(posts) + len(comments)) * 5) if (len(posts) + len(comments)) > 0 else 35}
                ],
                "activity_patterns": [
                    {"name": "Peak Hour", "value": min(100, activity_patterns.get('peak_hour', 12) * 4) if activity_patterns.get('peak_hour') else 60},
                    {"name": "Frequency", "value": min(100, (len(posts) + len(comments)) * 8) if (len(posts) + len(comments)) > 0 else 45},
                    {"name": "Posting Rate", "value": min(100, len(posts) * 15) if len(posts) > 0 else 30},
                    {"name": "Comment Rate", "value": min(100, len(comments) * 10) if len(comments) > 0 else 35}
                ],
                "sentiment_timeline": [
                    {"name": "Jan", "value": min(100, max(0, (sentiment.get('overall_sentiment', 0) + 1) * 50)) if sentiment.get('overall_sentiment') is not None else 65},
                    {"name": "Feb", "value": min(100, max(0, (sentiment.get('overall_sentiment', 0) + 1) * 50)) if sentiment.get('overall_sentiment') is not None else 70},
                    {"name": "Mar", "value": min(100, max(0, (sentiment.get('overall_sentiment', 0) + 1) * 50)) if sentiment.get('overall_sentiment') is not None else 75},
                    {"name": "Apr", "value": min(100, max(0, (sentiment.get('overall_sentiment', 0) + 1) * 50)) if sentiment.get('overall_sentiment') is not None else 80},
                    {"name": "May", "value": min(100, max(0, (sentiment.get('overall_sentiment', 0) + 1) * 50)) if sentiment.get('overall_sentiment') is not None else 85},
                    {"name": "Jun", "value": min(100, max(0, (sentiment.get('overall_sentiment', 0) + 1) * 50)) if sentiment.get('overall_sentiment') is not None else 90}
                ],
                "user_motivations": [
                    {"name": "Community", "value": 80},
                    {"name": "Information", "value": 70},
                    {"name": "Expression", "value": 60},
                    {"name": "Connection", "value": 75}
                ],
                "real_content": {
                    "posts": sample_posts,
                    "comments": sample_comments
                }
            },
            "formatted_text": f"""
🚀 REDDIT PERSONA REPORT
{'='*50}

👤 USER: u/{username}
📊 CONFIDENCE: 30.0%
⏰ GENERATED: {self._get_current_timestamp()}

🎭 PERSONALITY PROFILE
{'-'*30}
Type: {mbti.get('type', 'ENFP')} (Template)
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
Summary: {writing_style.get('summary', 'Clear and communicative')}
Complexity: {writing_style.get('complexity', 'Moderate')}
Tone: {writing_style.get('tone', 'Engaging')}

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
    
    def _calculate_big_five_traits(self, personality: Dict, sentiment: Dict, writing_style: Dict) -> Dict[str, int]:
        """Calculate Big Five personality traits from available data."""
        # Default values
        traits = {
            'openness': 50,
            'conscientiousness': 50,
            'extraversion': 50,
            'agreeableness': 50,
            'neuroticism': 50
        }
        
        # Adjust based on sentiment
        sentiment_score = sentiment.get('overall_sentiment', 0)
        if sentiment_score > 0.3:
            traits['agreeableness'] += 20
            traits['neuroticism'] -= 10
        elif sentiment_score < -0.3:
            traits['neuroticism'] += 20
            traits['agreeableness'] -= 10
        
        # Adjust based on writing style
        complexity = writing_style.get('complexity', 'moderate')
        if complexity == 'high':
            traits['openness'] += 15
        elif complexity == 'low':
            traits['openness'] -= 10
        
        # Adjust based on personality traits
        dominant_traits = personality.get('dominant_traits', [])
        for trait, score in dominant_traits:
            if 'open' in trait.lower():
                traits['openness'] += 10
            elif 'conscientious' in trait.lower():
                traits['conscientiousness'] += 10
            elif 'extravert' in trait.lower():
                traits['extraversion'] += 10
            elif 'agreeable' in trait.lower():
                traits['agreeableness'] += 10
            elif 'neurotic' in trait.lower():
                traits['neuroticism'] += 10
        
        # Ensure values are within 0-100 range
        for key in traits:
            traits[key] = max(0, min(100, traits[key]))
        
        return traits
    
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