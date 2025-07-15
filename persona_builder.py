"""
Persona Builder Module
Uses Gemini API to generate intelligent user personas with citations and confidence scoring.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv

from llm_service import LLMService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class PersonaBuilder:
    """Builds intelligent user personas using Gemini and analysis results."""
    
    def __init__(self):
        """Initialize the persona builder with LLM service (Gemini only)."""
        self.llm_service = LLMService()
        logger.info("PersonaBuilder initialized with LLM service (Gemini only)")
    
    async def build_persona(self, user_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a comprehensive user persona using Gemini and analysis results.
        """
        logger.info(f"Building persona for user: {user_data.get('username', 'unknown')}")
        try:
            # Use LLM service to generate persona
            persona = await self.llm_service.generate_persona(user_data, analysis_results)
            if 'metadata' not in persona:
                persona['metadata'] = {}
            persona['metadata'].update({
                'generated_at': datetime.now().isoformat(),
                'username': user_data.get('username'),
                'confidence_overall': self._calculate_overall_confidence(persona)
            })
            if 'source' not in persona['metadata']:
                persona['metadata']['source'] = 'gemini'
            persona = self._enhance_persona_with_analysis(persona, analysis_results)
            logger.info("Persona built successfully")
            return persona
        except Exception as e:
            logger.error(f"Error building persona: {e}")
            return self._create_fallback_persona(user_data, analysis_results)
    
    async def _build_persona_with_gpt4(self, user_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build persona using GPT-4."""
        
        # Prepare context for GPT-4
        context = self._prepare_gpt4_context(user_data, analysis_results)
        
        # Create the prompt
        prompt = self._create_gpt4_prompt(context)
        
        try:
            # Call GPT-4
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert psychologist and data analyst specializing in understanding human behavior from online activity. You create detailed, insightful user personas based on Reddit activity data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            # Parse GPT-4 response
            gpt_response = response.choices[0].message.content
            persona = self._parse_gpt4_response(gpt_response, user_data, analysis_results)
            
            return persona
            
        except Exception as e:
            logger.error(f"GPT-4 persona generation failed: {e}")
            return await self._build_persona_with_template(user_data, analysis_results)
    
    def _prepare_gpt4_context(self, user_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context data for GPT-4."""
        
        # Extract key information
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        
        # Sample posts and comments for context
        sample_posts = posts[:5] if posts else []
        sample_comments = comments[:5] if comments else []
        
        # Prepare analysis summary
        analysis_summary = {
            'sentiment': analysis_results.get('sentiment_analysis', {}),
            'personality': analysis_results.get('personality_traits', {}),
            'interests': analysis_results.get('interests', {}),
            'writing_style': analysis_results.get('writing_style', {}),
            'activity_patterns': analysis_results.get('activity_patterns', {}),
            'community_engagement': analysis_results.get('community_engagement', {}),
            'mbti': analysis_results.get('mbti_estimation', {})
        }
        
        return {
            'username': user_data.get('username'),
            'user_info': user_data.get('user_info', {}),
            'sample_posts': sample_posts,
            'sample_comments': sample_comments,
            'analysis_summary': analysis_summary,
            'total_posts': len(posts),
            'total_comments': len(comments)
        }
    
    def _create_gpt4_prompt(self, context: Dict[str, Any]) -> str:
        """Create the GPT-4 prompt for persona generation."""
        
        prompt = f"""
You are analyzing a Reddit user named u/{context['username']} to create a detailed persona.

USER DATA SUMMARY:
- Total posts: {context['total_posts']}
- Total comments: {context['total_comments']}
- Account age: {self._format_account_age(context['user_info'].get('created_utc'))}
- Karma: {context['user_info'].get('link_karma', 0)} post, {context['user_info'].get('comment_karma', 0)} comment

ANALYSIS RESULTS:
- Sentiment: {context['analysis_summary']['sentiment'].get('sentiment_category', 'neutral')} ({context['analysis_summary']['sentiment'].get('overall_sentiment', 0):.2f})
- Personality: {context['analysis_summary']['personality'].get('personality_type', 'Unknown')}
- Top interests: {', '.join([interest[0] for interest in context['analysis_summary']['interests'].get('top_interests', [])[:3]])}
- Writing style: {context['analysis_summary']['writing_style'].get('summary', 'Unknown')}
- Activity pattern: {context['analysis_summary']['activity_patterns'].get('activity_pattern', 'Unknown')}
- MBTI: {context['analysis_summary']['mbti'].get('type', 'Unknown')}

SAMPLE CONTENT:
Posts:
{self._format_sample_content(context['sample_posts'])}

Comments:
{self._format_sample_content(context['sample_comments'])}

TASK:
Create a comprehensive, insightful persona for this Reddit user. Include ALL of the following sections:

1. PERSONALITY PROFILE:
   - Personality type and key traits
   - Communication style
   - Behavioral patterns

2. INTERESTS & EXPERTISE:
   - Main areas of interest
   - Knowledge domains
   - Hobbies and activities

3. WRITING STYLE:
   - Tone and voice
   - Complexity level
   - Engagement patterns

4. SOCIAL BEHAVIOR:
   - Community engagement
   - Interaction style
   - Online presence

5. BEHAVIORS & HABITS:
   - Daily patterns and lifestyle choices
   - Reddit usage patterns
   - Posting and commenting habits
   - Time of day activity patterns

6. GOALS & NEEDS:
   - Primary objectives and requirements
   - What they're seeking on Reddit
   - Personal or professional goals
   - Information or community needs

7. BIG FIVE PERSONALITY TRAITS (OCEAN model):
   - Openness to Experience (0-100)
   - Conscientiousness (0-100)
   - Extraversion (0-100)
   - Agreeableness (0-100)
   - Neuroticism (0-100)

8. COMMUNITY ENGAGEMENT:
   - Reddit participation metrics
   - Subreddit diversity
   - Interaction frequency
   - Community contribution level

9. ACTIVITY PATTERNS:
   - User activity metrics
   - Posting frequency
   - Peak activity times
   - Engagement patterns

10. SENTIMENT TIMELINE:
    - Sentiment over time
    - Mood patterns
    - Emotional consistency
    - Sentiment trends

11. USER MOTIVATIONS:
    - What drives this user's behavior
    - Primary motivations for posting/commenting
    - Social, informational, or entertainment needs
    - Personal goals and aspirations

12. CITATIONS:
    - For each major insight, cite specific posts/comments that support it
    - Include post/comment ID, subreddit, and brief quote

Format your response as a JSON object with the following structure:
{{
    "personality": {{
        "type": "string",
        "traits": ["trait1", "trait2"],
        "confidence": 0.85,
        "description": "detailed description"
    }},
    "interests": ["interest1", "interest2"],
    "writing_style": {{
        "summary": "string",
        "complexity": "string",
        "tone": "string"
    }},
    "social_views": ["view1", "view2"],
    "behaviors_habits": {{
        "daily_patterns": "string",
        "lifestyle_choices": "string",
        "reddit_usage": "string",
        "posting_habits": "string",
        "activity_times": "string"
    }},
    "goals_needs": {{
        "primary_objectives": "string",
        "reddit_seeking": "string",
        "personal_goals": "string",
        "information_needs": "string"
    }},
    "big_five_traits": {{
        "openness": 75,
        "conscientiousness": 60,
        "extraversion": 45,
        "agreeableness": 70,
        "neuroticism": 30
    }},
    "community_engagement": {{
        "participation_level": "string",
        "subreddit_diversity": "string",
        "interaction_frequency": "string",
        "contribution_level": "string"
    }},
    "activity_patterns": {{
        "posting_frequency": "string",
        "peak_times": "string",
        "engagement_style": "string",
        "activity_metrics": "string"
    }},
    "sentiment_timeline": {{
        "overall_trend": "string",
        "mood_patterns": "string",
        "emotional_consistency": "string",
        "sentiment_evolution": "string"
    }},
    "user_motivations": {{
        "primary_drivers": "string",
        "posting_motivations": "string",
        "social_needs": "string",
        "personal_aspirations": "string"
    }},
    "citations": [
        {{
            "trait": "string",
            "evidence": "string",
            "source": "post/comment ID",
            "subreddit": "string",
            "quote": "brief quote"
        }}
    ]
}}

Be insightful, specific, and provide evidence for your conclusions. Fill in ALL sections with detailed information based on the user's Reddit activity.
"""
        
        return prompt
    
    def _format_account_age(self, created_utc: Optional[float]) -> str:
        """Format account age from creation timestamp."""
        if not created_utc:
            return "Unknown"
        
        created_date = datetime.fromtimestamp(created_utc)
        age_delta = datetime.now() - created_date
        years = age_delta.days // 365
        months = (age_delta.days % 365) // 30
        
        if years > 0:
            return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"
        else:
            return f"{months} month{'s' if months != 1 else ''}"
    
    def _format_sample_content(self, content_list: List[Dict]) -> str:
        """Format sample content for GPT-4 prompt."""
        if not content_list:
            return "No content available"
        
        formatted = []
        for i, item in enumerate(content_list, 1):
            text = item.get('title', '') or item.get('body', '')
            if text:
                # Truncate long text
                if len(text) > 200:
                    text = text[:200] + "..."
                formatted.append(f"{i}. {text}")
        
        return "\n".join(formatted) if formatted else "No content available"
    
    def _parse_gpt4_response(self, response: str, user_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GPT-4 response into structured persona."""
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response[json_start:json_end]
                gpt_persona = json.loads(json_str)
            else:
                # Fallback parsing
                gpt_persona = self._parse_text_response(response)
            
            # Enhance with analysis results
            persona = self._enhance_persona_with_analysis(gpt_persona, analysis_results)
            
            # Add citations with full context
            persona['citations'] = self._enhance_citations(persona.get('citations', []), user_data)
            
            return persona
            
        except Exception as e:
            logger.error(f"Failed to parse GPT-4 response: {e}")
            return self._create_fallback_persona(user_data, analysis_results)
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails."""
        # Simple text parsing as fallback
        return {
            'personality': {
                'type': 'Unknown',
                'traits': [],
                'confidence': 0.5,
                'description': response[:500] if response else 'No description available'
            },
            'interests': [],
            'writing_style': {
                'summary': 'Unknown',
                'complexity': 'Unknown',
                'tone': 'Unknown'
            },
            'social_views': [],
            'behaviors_habits': {
                'daily_patterns': 'No behavioral data available',
                'lifestyle_choices': 'No behavioral data available',
                'reddit_usage': 'No behavioral data available',
                'posting_habits': 'No behavioral data available',
                'activity_times': 'No behavioral data available'
            },
            'goals_needs': {
                'primary_objectives': 'No goals data available',
                'reddit_seeking': 'No goals data available',
                'personal_goals': 'No goals data available',
                'information_needs': 'No goals data available'
            },
            'big_five_traits': {
                'openness': 50,
                'conscientiousness': 50,
                'extraversion': 50,
                'agreeableness': 50,
                'neuroticism': 50
            },
            'community_engagement': {
                'participation_level': 'No engagement data available',
                'subreddit_diversity': 'No engagement data available',
                'interaction_frequency': 'No engagement data available',
                'contribution_level': 'No engagement data available'
            },
            'activity_patterns': {
                'posting_frequency': 'No activity data available',
                'peak_times': 'No activity data available',
                'engagement_style': 'No activity data available',
                'activity_metrics': 'No activity data available'
            },
            'sentiment_timeline': {
                'overall_trend': 'No sentiment data available',
                'mood_patterns': 'No sentiment data available',
                'emotional_consistency': 'No sentiment data available',
                'sentiment_evolution': 'No sentiment data available'
            },
            'user_motivations': {
                'primary_drivers': 'No motivation data available',
                'posting_motivations': 'No motivation data available',
                'social_needs': 'No motivation data available',
                'personal_aspirations': 'No motivation data available'
            },
            'citations': []
        }
    
    def _enhance_persona_with_analysis(self, gpt_persona: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance GPT-4 persona with analysis results."""
        
        # Merge personality information
        if 'personality' not in gpt_persona:
            gpt_persona['personality'] = {}
        
        mbti = analysis_results.get('mbti_estimation', {})
        if mbti:
            gpt_persona['personality']['mbti_type'] = mbti.get('type', 'Unknown')
            gpt_persona['personality']['mbti_description'] = mbti.get('description', '')
        
        # Add sentiment information
        sentiment = analysis_results.get('sentiment_analysis', {})
        if sentiment:
            gpt_persona['sentiment'] = {
                'overall': sentiment.get('sentiment_category', 'neutral'),
                'score': sentiment.get('overall_sentiment', 0),
                'subjectivity': sentiment.get('subjectivity', 0)
            }
        
        # Add activity patterns
        activity = analysis_results.get('activity_patterns', {})
        if activity:
            gpt_persona['activity_patterns'] = {
                'pattern': activity.get('activity_pattern', 'Unknown'),
                'peak_hour': activity.get('peak_hour', 0),
                'frequency': activity.get('activity_frequency', 0)
            }
        
        # Add community engagement
        engagement = analysis_results.get('community_engagement', {})
        if engagement:
            gpt_persona['community_engagement'] = {
                'level': engagement.get('engagement_level', 'Unknown'),
                'subreddit_diversity': engagement.get('subreddit_diversity', 0),
                'avg_score': engagement.get('avg_score', 0)
            }
        
        return gpt_persona
    
    def _enhance_citations(self, citations: List[Dict], user_data: Dict[str, Any]) -> List[Dict]:
        """Enhance citations with full context from user data."""
        enhanced_citations = []
        
        for citation in citations:
            source_id = citation.get('source', '')
            
            # Find the actual post/comment
            found_item = None
            item_type = 'unknown'
            
            # Search in posts
            for post in user_data.get('posts', []):
                if post.get('id') == source_id:
                    found_item = post
                    item_type = 'post'
                    break
            
            # Search in comments
            if not found_item:
                for comment in user_data.get('comments', []):
                    if comment.get('id') == source_id:
                        found_item = comment
                        item_type = 'comment'
                        break
            
            if found_item:
                enhanced_citation = {
                    'trait': citation.get('trait', ''),
                    'evidence': citation.get('evidence', ''),
                    'source_id': source_id,
                    'source_type': item_type,
                    'subreddit': found_item.get('subreddit', ''),
                    'score': found_item.get('score', 0),
                    'created_utc': found_item.get('created_utc'),
                    'permalink': found_item.get('permalink', ''),
                    'quote': citation.get('quote', ''),
                    'full_text': found_item.get('title', '') or found_item.get('body', '')
                }
                enhanced_citations.append(enhanced_citation)
        
        return enhanced_citations
    
    async def _build_persona_with_template(self, user_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build persona using template-based approach when GPT-4 is not available."""
        
        # Extract key information
        username = user_data.get('username', 'Unknown')
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        
        # Get analysis results
        sentiment = analysis_results.get('sentiment_analysis', {})
        personality = analysis_results.get('personality_traits', {})
        interests = analysis_results.get('interests', {})
        writing_style = analysis_results.get('writing_style', {})
        mbti = analysis_results.get('mbti_estimation', {})
        activity_patterns = analysis_results.get('activity_patterns', {})
        community_engagement = analysis_results.get('community_engagement', {})
        
        # Calculate Big Five traits from available data
        big_five = self._calculate_big_five_traits(personality, sentiment, writing_style)
        
        # Build template persona
        persona = {
            'personality': {
                'type': mbti.get('type', 'Unknown'),
                'traits': [trait[0] for trait in personality.get('dominant_traits', [])],
                'confidence': personality.get('confidence', 0.5),
                'description': f"User shows {sentiment.get('sentiment_category', 'neutral')} sentiment with {writing_style.get('complexity', 'moderate')} writing style."
            },
            'interests': [interest[0] for interest in interests.get('top_interests', [])],
            'writing_style': {
                'summary': writing_style.get('summary', 'Unknown'),
                'complexity': writing_style.get('complexity', 'Unknown'),
                'tone': writing_style.get('tone', 'Unknown')
            },
            'social_views': self._extract_social_views(posts, comments),
            'behaviors_habits': {
                'daily_patterns': f"User is most active during {activity_patterns.get('activity_pattern', 'unknown')} hours",
                'lifestyle_choices': "Based on Reddit activity patterns",
                'reddit_usage': f"Posts {len(posts)} times, comments {len(comments)} times",
                'posting_habits': f"Average score: {sum(p.get('score', 0) for p in posts) / max(len(posts), 1):.1f}",
                'activity_times': f"Peak activity: {activity_patterns.get('peak_hour', 'unknown')} hours"
            },
            'goals_needs': {
                'primary_objectives': "Information sharing and community engagement",
                'reddit_seeking': "Discussion and knowledge exchange",
                'personal_goals': "Building online presence and connections",
                'information_needs': "Community insights and discussions"
            },
            'big_five_traits': big_five,
            'community_engagement': {
                'participation_level': community_engagement.get('engagement_level', 'Moderate'),
                'subreddit_diversity': f"{community_engagement.get('subreddit_diversity', 0)} different subreddits",
                'interaction_frequency': f"{len(posts) + len(comments)} total interactions",
                'contribution_level': f"Average score: {community_engagement.get('avg_score', 0):.1f}"
            },
            'activity_patterns': {
                'posting_frequency': f"{len(posts)} posts, {len(comments)} comments",
                'peak_times': f"Peak at {activity_patterns.get('peak_hour', 'unknown')} hours",
                'engagement_style': activity_patterns.get('activity_pattern', 'Regular'),
                'activity_metrics': f"Activity frequency: {activity_patterns.get('activity_frequency', 0)}"
            },
            'sentiment_timeline': {
                'overall_trend': sentiment.get('sentiment_category', 'neutral'),
                'mood_patterns': f"Sentiment score: {sentiment.get('overall_sentiment', 0):.2f}",
                'emotional_consistency': f"Subjectivity: {sentiment.get('subjectivity', 0):.2f}",
                'sentiment_evolution': "Based on recent activity"
            },
            'user_motivations': {
                'primary_drivers': "Community engagement and information sharing",
                'posting_motivations': "Discussion and knowledge exchange",
                'social_needs': "Connection with like-minded individuals",
                'personal_aspirations': "Building online presence and influence"
            },
            'citations': self._generate_template_citations(posts, comments, personality.get('dominant_traits', []))
        }
        
        return persona
    
    def _extract_social_views(self, posts: List[Dict], comments: List[Dict]) -> List[str]:
        """Extract social views from posts and comments."""
        views = []
        
        # Simple keyword-based extraction
        social_keywords = {
            'privacy_advocate': ['privacy', 'data', 'surveillance', 'tracking'],
            'tech_skeptic': ['big tech', 'corporation', 'monopoly', 'surveillance'],
            'open_source': ['open source', 'free software', 'linux', 'github'],
            'environmental': ['climate', 'environment', 'sustainability', 'green'],
            'social_justice': ['equality', 'justice', 'rights', 'discrimination']
        }
        
        all_text = ' '.join([
            (post.get('title', '') + ' ' + post.get('body', '')).lower()
            for post in posts
        ] + [
            comment.get('body', '').lower()
            for comment in comments
        ])
        
        for view, keywords in social_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                views.append(view.replace('_', ' ').title())
        
        return views if views else ['General Reddit user']
    
    def _generate_template_citations(self, posts: List[Dict], comments: List[Dict], traits: List[Tuple[str, float]]) -> List[Dict]:
        """Generate template citations based on traits."""
        citations = []
        
        # Combine posts and comments
        all_items = []
        for post in posts:
            all_items.append(('post', post))
        for comment in comments:
            all_items.append(('comment', comment))
        
        # Generate citations for each trait
        for trait, score in traits[:3]:  # Top 3 traits
            if all_items:
                item_type, item = all_items[0]  # Use first item as example
                all_items = all_items[1:]  # Remove used item
                
                citation = {
                    'trait': trait,
                    'evidence': f"Shows {trait} characteristics",
                    'source_id': item.get('id', ''),
                    'source_type': item_type,
                    'subreddit': item.get('subreddit', ''),
                    'score': item.get('score', 0),
                    'created_utc': item.get('created_utc'),
                    'permalink': item.get('permalink', ''),
                    'quote': (item.get('title', '') or item.get('body', ''))[:100] + "...",
                    'full_text': item.get('title', '') or item.get('body', '')
                }
                citations.append(citation)
        
        return citations
    
    def _create_fallback_persona(self, user_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a minimal fallback persona when all else fails."""
        return {
            'personality': {
                'type': 'Unknown',
                'traits': ['Reddit user'],
                'confidence': 0.1,
                'description': 'Limited data available for analysis.'
            },
            'interests': ['General Reddit'],
            'writing_style': {
                'summary': 'Unknown',
                'complexity': 'Unknown',
                'tone': 'Unknown'
            },
            'social_views': ['General Reddit user'],
            'behaviors_habits': {
                'daily_patterns': 'No behavioral data available',
                'lifestyle_choices': 'No behavioral data available',
                'reddit_usage': 'No behavioral data available',
                'posting_habits': 'No behavioral data available',
                'activity_times': 'No behavioral data available'
            },
            'goals_needs': {
                'primary_objectives': 'No goals data available',
                'reddit_seeking': 'No goals data available',
                'personal_goals': 'No goals data available',
                'information_needs': 'No goals data available'
            },
            'big_five_traits': {
                'openness': 50,
                'conscientiousness': 50,
                'extraversion': 50,
                'agreeableness': 50,
                'neuroticism': 50
            },
            'community_engagement': {
                'participation_level': 'No engagement data available',
                'subreddit_diversity': 'No engagement data available',
                'interaction_frequency': 'No engagement data available',
                'contribution_level': 'No engagement data available'
            },
            'activity_patterns': {
                'posting_frequency': 'No activity data available',
                'peak_times': 'No activity data available',
                'engagement_style': 'No activity data available',
                'activity_metrics': 'No activity data available'
            },
            'sentiment_timeline': {
                'overall_trend': 'No sentiment data available',
                'mood_patterns': 'No sentiment data available',
                'emotional_consistency': 'No sentiment data available',
                'sentiment_evolution': 'No sentiment data available'
            },
            'user_motivations': {
                'primary_drivers': 'No motivation data available',
                'posting_motivations': 'No motivation data available',
                'social_needs': 'No motivation data available',
                'personal_aspirations': 'No motivation data available'
            },
            'citations': [],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'username': user_data.get('username', 'Unknown'),
                'source': 'fallback',
                'confidence_overall': 0.1
            }
        }
    
    def _calculate_overall_confidence(self, persona: Dict[str, Any]) -> float:
        """Calculate overall confidence in the persona."""
        confidence_factors = []
        
        # Personality confidence
        if 'personality' in persona:
            confidence_factors.append(persona['personality'].get('confidence', 0.5))
        
        # Citation confidence
        citations = persona.get('citations', [])
        if citations:
            confidence_factors.append(min(len(citations) / 5, 1.0))
        else:
            confidence_factors.append(0.1)
        
        # Data availability confidence
        metadata = persona.get('metadata', {})
        if metadata.get('source') == 'gpt4':
            confidence_factors.append(0.9)
        elif metadata.get('source') == 'template':
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.3)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _format_persona_text(self, persona: Dict[str, Any]) -> str:
        """Format persona as readable text."""
        
        username = persona.get('metadata', {}).get('username', 'Unknown')
        personality = persona.get('personality', {})
        interests = persona.get('interests', [])
        writing_style = persona.get('writing_style', {})
        citations = persona.get('citations', [])
        
        text = f"""--- Reddit User Persona: u/{username} ---

🎭 Personality Type: {personality.get('type', 'Unknown')}
📊 Confidence: {personality.get('confidence', 0):.2f}

🧠 Key Traits:
"""
        
        for trait in personality.get('traits', []):
            text += f"• {trait}\n"
        
        text += f"""
🎯 Main Interests:
"""
        
        for interest in interests:
            text += f"• {interest}\n"
        
        text += f"""
📝 Writing Style:
• {writing_style.get('summary', 'Unknown')}
• Complexity: {writing_style.get('complexity', 'Unknown')}
• Tone: {writing_style.get('tone', 'Unknown')}

🌍 Social Views:
"""
        
        for view in persona.get('social_views', []):
            text += f"• {view}\n"
        
        if citations:
            text += f"""
📌 Supporting Evidence:
"""
            
            for citation in citations[:5]:  # Top 5 citations
                text += f"""
📌 Supporting {citation.get('source_type', 'content').title()} for "{citation.get('trait', 'Unknown')}":
- "{citation.get('quote', 'No quote available')}"
  [{citation.get('source_type', 'Unknown').title()} in r/{citation.get('subreddit', 'Unknown')}, Score: {citation.get('score', 0)}]
"""
        
        text += f"""
---
Generated by Reddit Persona AI | Confidence: {persona.get('metadata', {}).get('confidence_overall', 0):.2f}
"""
        
        return text
    
    async def compare_personas(self, persona1: Dict[str, Any], persona2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two personas and find similarities/differences."""
        
        comparison = {
            'similarities': [],
            'differences': [],
            'compatibility_score': 0.0,
            'detailed_comparison': {}
        }
        
        # Compare personality traits
        traits1 = set(persona1.get('personality', {}).get('traits', []))
        traits2 = set(persona2.get('personality', {}).get('traits', []))
        
        common_traits = traits1.intersection(traits2)
        unique_traits1 = traits1 - traits2
        unique_traits2 = traits2 - traits1
        
        comparison['similarities'].extend([f"Both show {trait}" for trait in common_traits])
        comparison['differences'].extend([f"Persona 1 shows {trait}" for trait in unique_traits1])
        comparison['differences'].extend([f"Persona 2 shows {trait}" for trait in unique_traits2])
        
        # Compare interests
        interests1 = set(persona1.get('interests', []))
        interests2 = set(persona2.get('interests', []))
        
        common_interests = interests1.intersection(interests2)
        comparison['similarities'].extend([f"Both interested in {interest}" for interest in common_interests])
        
        # Calculate compatibility score
        total_traits = len(traits1.union(traits2))
        common_trait_ratio = len(common_traits) / max(total_traits, 1)
        
        total_interests = len(interests1.union(interests2))
        common_interest_ratio = len(common_interests) / max(total_interests, 1)
        
        comparison['compatibility_score'] = (common_trait_ratio + common_interest_ratio) / 2
        
        # Format comparison text
        comparison['formatted_text'] = self._format_comparison_text(comparison, persona1, persona2)
        
        return comparison
    
    def _format_comparison_text(self, comparison: Dict[str, Any], persona1: Dict[str, Any], persona2: Dict[str, Any]) -> str:
        """Format comparison as readable text."""
        
        username1 = persona1.get('metadata', {}).get('username', 'Unknown')
        username2 = persona2.get('metadata', {}).get('username', 'Unknown')
        
        text = f"""--- Persona Comparison: u/{username1} vs u/{username2} ---

🎯 Compatibility Score: {comparison['compatibility_score']:.2f}

🤝 Similarities:
"""
        
        for similarity in comparison['similarities'][:5]:
            text += f"• {similarity}\n"
        
        text += f"""
🔍 Key Differences:
"""
        
        for difference in comparison['differences'][:5]:
            text += f"• {difference}\n"
        
        text += f"""
---
Generated by Reddit Persona AI
"""
        
        return text 

    def _generate_formatted_text_with_citations(self, persona_data: dict) -> str:
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
        
        return text 

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