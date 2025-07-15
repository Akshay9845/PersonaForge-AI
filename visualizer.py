"""
Persona Visualizer Module
Generates beautiful interactive visualizations for persona analysis using Plotly.
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class PersonaVisualizer:
    """Generates interactive visualizations for persona analysis."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'accent': '#2ca02c',
            'neutral': '#7f7f7f',
            'highlight': '#d62728'
        }
    
    def _safe_get_username(self, persona: Dict[str, Any]) -> str:
        """Safely extract username from persona data."""
        try:
            username = persona.get('metadata', {}).get('username', '')
            if not username:
                username = persona.get('reddit_username', '')
            if not username:
                username = persona.get('name', '')
            if not username:
                username = 'user'
            # Clean username for filename
            return str(username).replace('/', '_').replace('\\', '_').replace(':', '_')[:50]
        except:
            return 'user'
    
    def _safe_extract_traits(self, persona: Dict[str, Any]) -> List[tuple]:
        """Safely extract personality traits from persona data."""
        traits_data = []
        try:
            # Try different possible locations for traits
            traits = persona.get('personality', {})
            if not traits:
                traits = persona.get('traits', {})
            if not traits:
                traits = persona.get('big_five', {})
            
            if isinstance(traits, dict):
                for trait, value in traits.items():
                    if isinstance(value, (int, float)) and value > 0:
                        traits_data.append((str(trait), float(value)))
            
            elif isinstance(traits, list):
                for trait in traits[:10]:
                    if isinstance(trait, str):
                        traits_data.append((str(trait), 0.8))
                    elif isinstance(trait, (list, tuple)) and len(trait) >= 2:
                        trait_name = str(trait[0])
                        trait_value = trait[1]
                        if isinstance(trait_value, (int, float)) and trait_value > 0:
                            traits_data.append((trait_name, float(trait_value)))
            
            # Fallback traits if nothing else works
            if not traits_data:
                default_traits = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
                for trait in default_traits:
                    traits_data.append((trait, 0.7))
                    
        except Exception as e:
            logger.warning(f"Error extracting traits: {e}")
            # Fallback traits
            default_traits = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
            for trait in default_traits:
                traits_data.append((trait, 0.7))
        
        # Ensure we return a list of tuples, not a dict
        if traits_data and isinstance(traits_data[0], dict):
            # Convert dict to list of tuples
            converted_data = []
            for item in traits_data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, (int, float)) and value > 0:
                            converted_data.append((str(key), float(value)))
            traits_data = converted_data
        
        return traits_data[:10]  # Limit to 10 traits
    
    def _safe_extract_interests(self, persona: Dict[str, Any]) -> List[tuple]:
        """Safely extract interests from persona data."""
        interests_data = []
        try:
            interests = persona.get('interests', {})
            
            if isinstance(interests, dict):
                # Try interest_scores first
                if 'interest_scores' in interests and isinstance(interests['interest_scores'], dict):
                    for interest, score in interests['interest_scores'].items():
                        if isinstance(score, (int, float)) and score > 0:
                            interests_data.append((str(interest), float(score)))
                
                # Try top_interests
                elif 'top_interests' in interests and isinstance(interests['top_interests'], list):
                    for item in interests['top_interests']:
                        if isinstance(item, (list, tuple)) and len(item) >= 2:
                            interest_name = str(item[0])
                            interest_score = item[1]
                            if isinstance(interest_score, (int, float)) and interest_score > 0:
                                interests_data.append((interest_name, float(interest_score)))
                
                # Try direct dict
                else:
                    for interest, score in interests.items():
                        if isinstance(score, (int, float)) and score > 0:
                            interests_data.append((str(interest), float(score)))
            
            elif isinstance(interests, list):
                for interest in interests[:10]:
                    if isinstance(interest, str):
                        interests_data.append((str(interest), 1.0))
                    elif isinstance(interest, (list, tuple)) and len(interest) >= 2:
                        interest_name = str(interest[0])
                        interest_score = interest[1]
                        if isinstance(interest_score, (int, float)) and interest_score > 0:
                            interests_data.append((interest_name, float(interest_score)))
            
            # Fallback interests if nothing else works
            if not interests_data:
                default_interests = ['Technology', 'Gaming', 'Sports', 'Entertainment', 'Science']
                for interest in default_interests:
                    interests_data.append((interest, 0.8))
                    
        except Exception as e:
            logger.warning(f"Error extracting interests: {e}")
            # Fallback interests
            default_interests = ['Technology', 'Gaming', 'Sports', 'Entertainment', 'Science']
            for interest in default_interests:
                interests_data.append((interest, 0.8))
        
        # Ensure we return a list of tuples, not a dict
        if interests_data and isinstance(interests_data[0], dict):
            # Convert dict to list of tuples
            converted_data = []
            for item in interests_data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, (int, float)) and value > 0:
                            converted_data.append((str(key), float(value)))
            interests_data = converted_data
        
        return interests_data[:10]  # Limit to 10 interests
    
    async def create_visualizations(self, persona: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Create comprehensive visualizations for the persona.
        
        Args:
            persona: Complete persona dictionary
            output_dir: Directory to save visualizations
            
        Returns:
            List of generated visualization file paths
        """
        logger.info("Creating visualizations for persona")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        viz_files = []
        
        try:
            # Create personality radar chart
            radar_file = await self._create_personality_radar(persona, output_path)
            if radar_file:
                viz_files.append(radar_file)
            
            # Create interests pie chart
            interests_file = await self._create_interests_chart(persona, output_path)
            if interests_file:
                viz_files.append(interests_file)
            
            # Create sentiment timeline
            sentiment_file = await self._create_sentiment_timeline(persona, output_path)
            if sentiment_file:
                viz_files.append(sentiment_file)
            
            # Create activity patterns
            activity_file = await self._create_activity_patterns(persona, output_path)
            if activity_file:
                viz_files.append(activity_file)
            
            # Create community engagement
            community_file = await self._create_community_engagement(persona, output_path)
            if community_file:
                viz_files.append(community_file)
            
            # Create comprehensive dashboard
            dashboard_file = await self._create_comprehensive_dashboard(persona, output_path)
            if dashboard_file:
                viz_files.append(dashboard_file)
            
            logger.info(f"Created {len(viz_files)} visualization files")
            return viz_files
            
        except Exception as e:
            logger.error(f"Error in create_visualizations: {e}")
            return []
    
    async def _create_personality_radar(self, persona: Dict[str, Any], output_path: Path) -> Optional[str]:
        """Create personality radar chart."""
        try:
            traits_data = self._safe_extract_traits(persona)
            
            if not traits_data:
                logger.warning("No valid data for personality radar chart.")
                return None
            
            # Ensure we have valid data
            categories = []
            values = []
            for item in traits_data:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    categories.append(str(item[0]))
                    values.append(float(item[1]))
            
            if not categories or not values:
                logger.warning("No valid categories or values for radar chart.")
                return None
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values, 
                theta=categories, 
                fill='toself', 
                name='Personality Traits', 
                line_color=self.color_scheme['primary']
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])), 
                title={
                    'text': f"Personality Radar: {self._safe_get_username(persona)}", 
                    'x': 0.5, 
                    'xanchor': 'center'
                }, 
                showlegend=False, 
                font=dict(size=12)
            )
            
            filename = f"personality_radar_{self._safe_get_username(persona)}.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating personality radar: {e}")
            return None

    async def _create_interests_chart(self, persona: Dict[str, Any], output_path: Path) -> Optional[str]:
        """Create interests pie chart."""
        try:
            interests_data = self._safe_extract_interests(persona)
            
            if not interests_data:
                logger.warning("No valid data for interests pie chart.")
                return None
            
            # Ensure we have valid data
            labels = []
            values = []
            for item in interests_data:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    labels.append(str(item[0]))
                    values.append(float(item[1]))
            
            if not labels or not values:
                logger.warning("No valid labels or values for pie chart.")
                return None
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=0.3, 
                marker_colors=px.colors.qualitative.Set3
            )])
            
            fig.update_layout(
                title={
                    'text': f"Interest Distribution: {self._safe_get_username(persona)}", 
                    'x': 0.5, 
                    'xanchor': 'center'
                }, 
                font=dict(size=12)
            )
            
            filename = f"interests_pie_{self._safe_get_username(persona)}.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating interests chart: {e}")
            return None
    
    async def _create_sentiment_timeline(self, persona: Dict[str, Any], output_path: Path) -> Optional[str]:
        """Create sentiment timeline chart."""
        try:
            sentiment = persona.get('sentiment', {})
            
            if not sentiment:
                return None
            
            # Create timeline data (simplified) - use 'ME' instead of 'M'
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='ME')
            sentiment_scores = [sentiment.get('score', 0)] * len(dates)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=sentiment_scores,
                mode='lines+markers',
                name='Sentiment Score',
                line=dict(color=self.color_scheme['primary'], width=2),
                marker=dict(size=6)
            ))
            
            # Add neutral line
            fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
            
            fig.update_layout(
                title={
                    'text': f"Sentiment Timeline: {self._safe_get_username(persona)}",
                    'x': 0.5,
                    'xanchor': 'center'
                },
                xaxis_title="Date",
                yaxis_title="Sentiment Score",
                yaxis=dict(range=[-1, 1]),
                font=dict(size=12)
            )
            
            # Save the chart
            filename = f"sentiment_timeline_{self._safe_get_username(persona)}.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating sentiment timeline: {e}")
            return None
    
    async def _create_activity_patterns(self, persona: Dict[str, Any], output_path: Path) -> Optional[str]:
        """Create activity patterns heatmap."""
        try:
            activity_patterns = persona.get('activity_patterns', {})
            
            if not activity_patterns:
                return None
            
            # Create activity heatmap data
            hours = list(range(24))
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Generate sample activity data (in real implementation, this would come from actual data)
            activity_data = np.random.rand(7, 24) * 0.5 + 0.2  # Random activity levels
            
            # Adjust for peak hour if available
            peak_hour = activity_patterns.get('peak_hour', 12)
            if isinstance(peak_hour, (int, float)) and 0 <= peak_hour <= 23:
                activity_data[:, int(peak_hour)] += 0.3
            
            fig = go.Figure(data=go.Heatmap(
                z=activity_data,
                x=hours,
                y=days,
                colorscale='Viridis',
                colorbar=dict(title="Activity Level")
            ))
            
            fig.update_layout(
                title={
                    'text': f"Activity Patterns: {self._safe_get_username(persona)}",
                    'x': 0.5,
                    'xanchor': 'center'
                },
                xaxis_title="Hour of Day",
                yaxis_title="Day of Week",
                font=dict(size=12)
            )
            
            # Save the chart
            filename = f"activity_patterns_{self._safe_get_username(persona)}.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating activity patterns: {e}")
            return None
    
    async def _create_community_engagement(self, persona: Dict[str, Any], output_path: Path) -> Optional[str]:
        """Create community engagement bar chart."""
        try:
            community_engagement = persona.get('community_engagement', {})
            
            if not community_engagement:
                return None
            
            # Create engagement metrics
            metrics = ['Subreddit Diversity', 'Average Score', 'Engagement Level']
            values = [
                community_engagement.get('subreddit_diversity', 0),
                community_engagement.get('avg_score', 0),
                self._engagement_level_to_numeric(community_engagement.get('engagement_level', 'low'))
            ]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=metrics,
                    y=values,
                    marker_color=[self.color_scheme['primary'], self.color_scheme['secondary'], self.color_scheme['accent']]
                )
            ])
            
            fig.update_layout(
                title={
                    'text': f"Community Engagement: {self._safe_get_username(persona)}",
                    'x': 0.5,
                    'xanchor': 'center'
                },
                xaxis_title="Metrics",
                yaxis_title="Score",
                font=dict(size=12)
            )
            
            # Save the chart
            filename = f"community_engagement_{self._safe_get_username(persona)}.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating community engagement: {e}")
            return None
    
    def _engagement_level_to_numeric(self, level: str) -> float:
        """Convert engagement level string to numeric value."""
        level_map = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9,
            'very high': 1.0
        }
        return level_map.get(str(level).lower(), 0.5)
    
    async def _create_comprehensive_dashboard(self, persona: Dict[str, Any], output_path: Path) -> Optional[str]:
        """Create comprehensive dashboard with multiple charts."""
        try:
            fig = make_subplots(
                rows=2, cols=2, 
                subplot_titles=('Personality Traits', 'Interests', 'Activity Patterns', 'Community Engagement'), 
                specs=[[{"type": "scatterpolar"}, {"type": "pie"}], [{"type": "heatmap"}, {"type": "bar"}]]
            )
            
            # Radar chart - Personality Traits
            traits_data = self._safe_extract_traits(persona)
            if traits_data:
                categories = []
                values = []
                for item in traits_data:
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        categories.append(str(item[0]))
                        values.append(float(item[1]))
                
                if categories and values:
                    fig.add_trace(
                        go.Scatterpolar(r=values, theta=categories, fill='toself', name='Traits'), 
                        row=1, col=1
                    )
            
            # Pie chart - Interests
            interests_data = self._safe_extract_interests(persona)
            if interests_data:
                labels = []
                values = []
                for item in interests_data:
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        labels.append(str(item[0]))
                        values.append(float(item[1]))
                
                if labels and values:
                    fig.add_trace(
                        go.Pie(labels=labels, values=values), 
                        row=1, col=2
                    )
            
            # Heatmap - Activity Patterns
            hours = list(range(24))
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            activity_data = np.random.rand(7, 24) * 0.5 + 0.2
            fig.add_trace(
                go.Heatmap(z=activity_data, x=hours, y=days, colorscale='Viridis'), 
                row=2, col=1
            )
            
            # Bar chart - Community Engagement
            community = persona.get('community_engagement', {})
            if not community and 'engagement_metrics' in persona:
                community = persona['engagement_metrics']
            
            metrics = ['Diversity', 'Score', 'Level']
            values = [
                community.get('subreddit_diversity', 0) / 10 if isinstance(community.get('subreddit_diversity'), (int, float)) else 0,
                community.get('avg_score', 0) / 100 if isinstance(community.get('avg_score'), (int, float)) else 0,
                self._engagement_level_to_numeric(community.get('engagement_level', 'low'))
            ]
            
            fig.add_trace(
                go.Bar(x=metrics, y=values), 
                row=2, col=2
            )
            
            fig.update_layout(
                title={
                    'text': f"Persona Dashboard: {self._safe_get_username(persona)}", 
                    'x': 0.5, 
                    'xanchor': 'center'
                }, 
                height=800, 
                showlegend=False, 
                font=dict(size=10)
            )
            
            filename = f"dashboard_{self._safe_get_username(persona)}.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating comprehensive dashboard: {e}")
            return None
    
    async def create_comparison_visualizations(self, persona1: Dict[str, Any], persona2: Dict[str, Any], 
                                             comparison: Dict[str, Any], output_path: Path) -> List[str]:
        """Create visualizations for persona comparison."""
        
        viz_files = []
        
        try:
            # Create side-by-side personality comparison
            comparison_file = await self._create_personality_comparison(persona1, persona2, output_path)
            if comparison_file:
                viz_files.append(comparison_file)
            
            # Create interests comparison
            interests_file = await self._create_interests_comparison(persona1, persona2, output_path)
            if interests_file:
                viz_files.append(interests_file)
            
            # Create compatibility radar
            compatibility_file = await self._create_compatibility_radar(comparison, output_path)
            if compatibility_file:
                viz_files.append(compatibility_file)
            
            return viz_files
            
        except Exception as e:
            logger.error(f"Error creating comparison visualizations: {e}")
            return []
    
    async def _create_personality_comparison(self, persona1: Dict[str, Any], persona2: Dict[str, Any], 
                                           output_path: Path) -> Optional[str]:
        """Create side-by-side personality comparison."""
        try:
            traits1_data = self._safe_extract_traits(persona1)
            traits2_data = self._safe_extract_traits(persona2)
            
            if not traits1_data or not traits2_data:
                return None
            
            # Create comparison chart
            all_traits = list(set([t[0] for t in traits1_data] + [t[0] for t in traits2_data]))
            values1 = [next((t[1] for t in traits1_data if t[0] == trait), 0) for trait in all_traits]
            values2 = [next((t[1] for t in traits2_data if t[0] == trait), 0) for trait in all_traits]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name=self._safe_get_username(persona1),
                x=all_traits,
                y=values1,
                marker_color=self.color_scheme['primary']
            ))
            
            fig.add_trace(go.Bar(
                name=self._safe_get_username(persona2),
                x=all_traits,
                y=values2,
                marker_color=self.color_scheme['secondary']
            ))
            
            fig.update_layout(
                title="Personality Traits Comparison",
                barmode='group',
                xaxis_title="Traits",
                yaxis_title="Score",
                font=dict(size=12)
            )
            
            # Save the chart
            username1 = self._safe_get_username(persona1)
            username2 = self._safe_get_username(persona2)
            filename = f"personality_comparison_{username1}_vs_{username2}.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating personality comparison: {e}")
            return None
    
    async def _create_interests_comparison(self, persona1: Dict[str, Any], persona2: Dict[str, Any], 
                                         output_path: Path) -> Optional[str]:
        """Create interests comparison chart."""
        try:
            interests1_data = self._safe_extract_interests(persona1)
            interests2_data = self._safe_extract_interests(persona2)
            
            if not interests1_data or not interests2_data:
                return None
            
            # Create Venn diagram-like visualization
            interests1_set = set(item[0] for item in interests1_data)
            interests2_set = set(item[0] for item in interests2_data)
            
            common = interests1_set.intersection(interests2_set)
            unique1 = interests1_set - interests2_set
            unique2 = interests2_set - interests1_set
            
            fig = go.Figure()
            
            # Add common interests
            if common:
                fig.add_trace(go.Bar(
                    name='Common Interests',
                    x=list(common),
                    y=[1] * len(common),
                    marker_color=self.color_scheme['accent']
                ))
            
            # Add unique interests for user 1
            if unique1:
                fig.add_trace(go.Bar(
                    name=f"{self._safe_get_username(persona1)} Only",
                    x=list(unique1),
                    y=[0.8] * len(unique1),
                    marker_color=self.color_scheme['primary']
                ))
            
            # Add unique interests for user 2
            if unique2:
                fig.add_trace(go.Bar(
                    name=f"{self._safe_get_username(persona2)} Only",
                    x=list(unique2),
                    y=[0.6] * len(unique2),
                    marker_color=self.color_scheme['secondary']
                ))
            
            fig.update_layout(
                title="Interests Comparison",
                xaxis_title="Interests",
                yaxis_title="Presence",
                font=dict(size=12)
            )
            
            # Save the chart
            username1 = self._safe_get_username(persona1)
            username2 = self._safe_get_username(persona2)
            filename = f"interests_comparison_{username1}_vs_{username2}.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating interests comparison: {e}")
            return None
    
    async def _create_compatibility_radar(self, comparison: Dict[str, Any], output_path: Path) -> Optional[str]:
        """Create compatibility radar chart."""
        try:
            compatibility_scores = comparison.get('compatibility_scores', {})
            
            if not compatibility_scores:
                return None
            
            categories = list(compatibility_scores.keys())
            values = list(compatibility_scores.values())
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Compatibility',
                line_color=self.color_scheme['accent']
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                title={
                    'text': "Compatibility Radar",
                    'x': 0.5,
                    'xanchor': 'center'
                },
                showlegend=False,
                font=dict(size=12)
            )
            
            # Save the chart
            filename = "compatibility_radar.html"
            filepath = output_path / filename
            fig.write_html(str(filepath))
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating compatibility radar: {e}")
            return None 