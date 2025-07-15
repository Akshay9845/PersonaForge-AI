"""
Persona Analyzer Module
Handles NLP analysis, sentiment analysis, topic modeling, and personality detection.
"""

import asyncio
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

logger = logging.getLogger(__name__)


class PersonaAnalyzer:
    """Analyzes Reddit user data to extract personality traits and patterns."""
    
    def __init__(self):
        """Initialize the analyzer with NLP tools."""
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        # Personality indicators
        self.personality_indicators = {
            'introvert': ['alone', 'quiet', 'private', 'reserved', 'shy', 'solitary'],
            'extrovert': ['social', 'outgoing', 'energetic', 'talkative', 'friendly', 'party'],
            'analytical': ['analysis', 'data', 'research', 'study', 'evidence', 'logical'],
            'creative': ['creative', 'art', 'design', 'imagination', 'original', 'unique'],
            'sarcastic': ['sarcasm', 'irony', 'sarcastic', 'joking', 'humor', 'wit'],
            'formal': ['formal', 'professional', 'proper', 'respectful', 'courteous'],
            'casual': ['casual', 'relaxed', 'informal', 'chill', 'laid-back', 'easy-going'],
            'confident': ['confident', 'sure', 'certain', 'definitely', 'absolutely'],
            'uncertain': ['maybe', 'perhaps', 'might', 'could', 'possibly', 'uncertain'],
            'positive': ['good', 'great', 'awesome', 'amazing', 'wonderful', 'excellent'],
            'negative': ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'frustrating']
        }
        
        # Interest categories
        self.interest_categories = {
            'technology': ['programming', 'coding', 'software', 'tech', 'computer', 'ai', 'machine learning'],
            'gaming': ['game', 'gaming', 'playstation', 'xbox', 'nintendo', 'steam', 'gamer'],
            'sports': ['football', 'basketball', 'soccer', 'baseball', 'tennis', 'sport', 'athlete'],
            'politics': ['politics', 'political', 'government', 'election', 'policy', 'democracy'],
            'science': ['science', 'scientific', 'research', 'study', 'experiment', 'discovery'],
            'entertainment': ['movie', 'film', 'music', 'tv', 'show', 'entertainment', 'celebrity'],
            'finance': ['money', 'finance', 'investment', 'stock', 'trading', 'economy'],
            'health': ['health', 'medical', 'fitness', 'exercise', 'diet', 'wellness'],
            'education': ['education', 'learning', 'school', 'university', 'study', 'academic'],
            'travel': ['travel', 'trip', 'vacation', 'destination', 'tourism', 'adventure']
        }
    
    async def analyze_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of user data.
        
        Args:
            user_data: Dictionary containing user posts and comments
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting analysis for user: {user_data.get('username', 'unknown')}")
        
        # Extract text data
        all_text = self._extract_text_data(user_data)
        
        if not all_text:
            logger.warning("No text data found for analysis")
            return self._empty_analysis_result()
        
        # Perform various analyses
        analysis_results = {
            'text_statistics': self._analyze_text_statistics(all_text),
            'sentiment_analysis': self._analyze_sentiment(all_text),
            'personality_traits': self._detect_personality_traits(all_text),
            'interests': self._detect_interests(all_text),
            'writing_style': self._analyze_writing_style(all_text),
            'activity_patterns': self._analyze_activity_patterns(user_data),
            'community_engagement': self._analyze_community_engagement(user_data),
            'topic_modeling': await self._perform_topic_modeling(all_text),
            'behavioral_clusters': self._create_behavioral_clusters(user_data),
            'mbti_estimation': self._estimate_mbti_type(all_text),
            'confidence_scores': {}
        }
        
        # Calculate confidence scores
        analysis_results['confidence_scores'] = self._calculate_confidence_scores(analysis_results)
        
        logger.info("Analysis completed successfully")
        return analysis_results
    
    def _extract_text_data(self, user_data: Dict[str, Any]) -> List[str]:
        """Extract and clean text data from user posts and comments."""
        text_data = []
        
        # Extract from posts
        for post in user_data.get('posts', []):
            if post.get('title'):
                text_data.append(post['title'])
            if post.get('body'):
                text_data.append(post['body'])
        
        # Extract from comments
        for comment in user_data.get('comments', []):
            if comment.get('body'):
                text_data.append(comment['body'])
        
        # Clean text data
        cleaned_text = []
        for text in text_data:
            if text and len(text.strip()) > 10:  # Filter out very short texts
                cleaned = self._clean_text(text)
                if cleaned:
                    cleaned_text.append(cleaned)
        
        return cleaned_text
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text."""
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
    
    def _analyze_text_statistics(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze basic text statistics."""
        if not texts:
            return {}
        
        all_text = ' '.join(texts)
        words = word_tokenize(all_text.lower())
        sentences = sent_tokenize(all_text)
        
        # Filter out stop words for meaningful word count
        meaningful_words = [word for word in words if word.isalpha() and word not in self.stop_words]
        
        stats = {
            'total_texts': len(texts),
            'total_words': len(words),
            'meaningful_words': len(meaningful_words),
            'total_sentences': len(sentences),
            'avg_words_per_text': len(words) / len(texts),
            'avg_sentences_per_text': len(sentences) / len(texts),
            'avg_words_per_sentence': len(words) / max(len(sentences), 1),
            'vocabulary_size': len(set(meaningful_words)),
            'lexical_diversity': len(set(meaningful_words)) / max(len(meaningful_words), 1),
            'avg_text_length': sum(len(text) for text in texts) / len(texts)
        }
        
        return stats
    
    def _analyze_sentiment(self, texts: List[str]) -> Dict[str, Any]:
        """Perform sentiment analysis on texts."""
        if not texts:
            return {}
        
        sentiments = []
        subjectivity_scores = []
        
        for text in texts:
            blob = TextBlob(text)
            sentiments.append(blob.sentiment.polarity)
            subjectivity_scores.append(blob.sentiment.subjectivity)
        
        # Calculate overall sentiment
        avg_sentiment = np.mean(sentiments)
        avg_subjectivity = np.mean(subjectivity_scores)
        
        # Determine sentiment category
        if avg_sentiment > 0.1:
            sentiment_category = 'positive'
        elif avg_sentiment < -0.1:
            sentiment_category = 'negative'
        else:
            sentiment_category = 'neutral'
        
        # Analyze sentiment trends
        sentiment_trends = self._analyze_sentiment_trends(sentiments)
        
        return {
            'overall_sentiment': avg_sentiment,
            'sentiment_category': sentiment_category,
            'subjectivity': avg_subjectivity,
            'sentiment_distribution': {
                'positive': len([s for s in sentiments if s > 0.1]),
                'neutral': len([s for s in sentiments if -0.1 <= s <= 0.1]),
                'negative': len([s for s in sentiments if s < -0.1])
            },
            'sentiment_trends': sentiment_trends,
            'confidence': min(abs(avg_sentiment) * 2, 1.0)  # Higher confidence for stronger sentiments
        }
    
    def _analyze_sentiment_trends(self, sentiments: List[float]) -> Dict[str, Any]:
        """Analyze sentiment trends over time."""
        if len(sentiments) < 2:
            return {}
        
        # Simple trend analysis
        recent_sentiments = sentiments[-10:]  # Last 10 texts
        older_sentiments = sentiments[:-10] if len(sentiments) > 10 else []
        
        recent_avg = np.mean(recent_sentiments) if recent_sentiments else 0
        older_avg = np.mean(older_sentiments) if older_sentiments else 0
        
        trend = 'stable'
        if recent_avg > older_avg + 0.1:
            trend = 'improving'
        elif recent_avg < older_avg - 0.1:
            trend = 'declining'
        
        return {
            'trend': trend,
            'recent_sentiment': recent_avg,
            'older_sentiment': older_avg,
            'change': recent_avg - older_avg
        }
    
    def _detect_personality_traits(self, texts: List[str]) -> Dict[str, Any]:
        """Detect personality traits from text analysis."""
        if not texts:
            return {}
        
        all_text = ' '.join(texts).lower()
        words = set(word_tokenize(all_text))
        
        trait_scores = {}
        
        for trait, indicators in self.personality_indicators.items():
            # Count occurrences of trait indicators
            count = sum(1 for indicator in indicators if indicator in words)
            # Normalize by text length
            score = count / max(len(texts), 1)
            trait_scores[trait] = min(score * 10, 1.0)  # Scale to 0-1
        
        # Determine dominant traits
        dominant_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate overall personality type
        personality_type = self._determine_personality_type(trait_scores)
        
        return {
            'trait_scores': trait_scores,
            'dominant_traits': dominant_traits,
            'personality_type': personality_type,
            'confidence': self._calculate_personality_confidence(trait_scores)
        }
    
    def _determine_personality_type(self, trait_scores: Dict[str, float]) -> str:
        """Determine overall personality type from trait scores."""
        # Simple personality type determination
        if trait_scores.get('introvert', 0) > trait_scores.get('extrovert', 0):
            base_type = 'I'
        else:
            base_type = 'E'
        
        if trait_scores.get('analytical', 0) > trait_scores.get('creative', 0):
            function_type = 'T'
        else:
            function_type = 'F'
        
        return f"{base_type}{function_type}XX"  # Simplified MBTI-like type
    
    def _calculate_personality_confidence(self, trait_scores: Dict[str, float]) -> float:
        """Calculate confidence in personality assessment."""
        if not trait_scores:
            return 0.0
        
        # Higher confidence if traits are more distinct
        max_score = max(trait_scores.values())
        avg_score = np.mean(list(trait_scores.values()))
        
        # Confidence based on how distinct the traits are
        confidence = (max_score - avg_score) * 2
        return min(confidence, 1.0)
    
    def _detect_interests(self, texts: List[str]) -> Dict[str, Any]:
        """Detect user interests from text analysis."""
        if not texts:
            return {}
        
        all_text = ' '.join(texts).lower()
        words = word_tokenize(all_text)
        
        interest_scores = {}
        
        for category, keywords in self.interest_categories.items():
            # Count keyword occurrences
            count = sum(1 for word in words if word in keywords)
            # Normalize by text length
            score = count / max(len(words), 1)
            interest_scores[category] = min(score * 100, 1.0)  # Scale to 0-1
        
        # Get top interests
        top_interests = sorted(interest_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'interest_scores': interest_scores,
            'top_interests': top_interests,
            'primary_interest': top_interests[0][0] if top_interests else 'general',
            'interest_diversity': len([score for score in interest_scores.values() if score > 0.1])
        }
    
    def _analyze_writing_style(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze writing style characteristics."""
        if not texts:
            return {}
        
        all_text = ' '.join(texts)
        
        # Analyze sentence structure
        sentences = sent_tokenize(all_text)
        avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
        
        # Analyze word complexity
        words = word_tokenize(all_text.lower())
        avg_word_length = np.mean([len(word) for word in words if word.isalpha()])
        
        # Analyze punctuation usage
        punctuation_count = len(re.findall(r'[.!?]', all_text))
        exclamation_count = len(re.findall(r'!', all_text))
        question_count = len(re.findall(r'\?', all_text))
        
        # Determine writing style
        if avg_sentence_length > 20:
            style_complexity = 'complex'
        elif avg_sentence_length > 15:
            style_complexity = 'moderate'
        else:
            style_complexity = 'simple'
        
        if exclamation_count > len(sentences) * 0.1:
            style_tone = 'enthusiastic'
        elif question_count > len(sentences) * 0.1:
            style_tone = 'inquisitive'
        else:
            style_tone = 'neutral'
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'complexity': style_complexity,
            'tone': style_tone,
            'punctuation_usage': {
                'total': punctuation_count,
                'exclamations': exclamation_count,
                'questions': question_count
            },
            'summary': f"{style_complexity.capitalize()} sentences with {style_tone} tone"
        }
    
    def _analyze_activity_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user activity patterns."""
        activities = user_data.get('posts', []) + user_data.get('comments', [])
        
        if not activities:
            return {}
        
        # Analyze timing patterns
        timestamps = []
        for activity in activities:
            if activity.get('created_utc'):
                timestamps.append(activity['created_utc'])
        
        if timestamps:
            # Convert to datetime objects
            dates = [datetime.fromtimestamp(ts) for ts in timestamps]
            
            # Analyze time of day
            hours = [date.hour for date in dates]
            hour_distribution = Counter(hours)
            
            # Determine peak activity time
            peak_hour = max(hour_distribution.items(), key=lambda x: x[1])[0]
            
            # Determine if user is a night owl or early bird
            night_activity = sum(1 for hour in hours if 22 <= hour or hour <= 6)
            day_activity = len(hours) - night_activity
            
            if night_activity > day_activity:
                activity_pattern = 'night_owl'
            elif day_activity > night_activity * 2:
                activity_pattern = 'early_bird'
            else:
                activity_pattern = 'balanced'
            
            return {
                'total_activities': len(activities),
                'activity_frequency': len(activities) / max(len(set([d.date() for d in dates])), 1),
                'peak_hour': peak_hour,
                'activity_pattern': activity_pattern,
                'hour_distribution': dict(hour_distribution),
                'night_activity_ratio': night_activity / len(hours)
            }
        
        return {}
    
    def _analyze_community_engagement(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's community engagement patterns."""
        activities = user_data.get('posts', []) + user_data.get('comments', [])
        
        if not activities:
            return {}
        
        # Analyze subreddit diversity
        subreddits = [act.get('subreddit', 'unknown') for act in activities]
        subreddit_counts = Counter(subreddits)
        
        # Calculate engagement metrics
        total_score = sum(act.get('score', 0) for act in activities)
        avg_score = total_score / len(activities)
        
        # Analyze comment vs post ratio
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        comment_ratio = len(comments) / max(len(activities), 1)
        
        return {
            'subreddit_diversity': len(subreddit_counts),
            'top_subreddits': subreddit_counts.most_common(5),
            'avg_score': avg_score,
            'total_score': total_score,
            'comment_ratio': comment_ratio,
            'engagement_level': self._determine_engagement_level(avg_score, len(activities))
        }
    
    def _determine_engagement_level(self, avg_score: float, activity_count: int) -> str:
        """Determine user's engagement level."""
        if avg_score > 50 and activity_count > 20:
            return 'high'
        elif avg_score > 10 and activity_count > 10:
            return 'moderate'
        else:
            return 'low'
    
    async def _perform_topic_modeling(self, texts: List[str]) -> Dict[str, Any]:
        """Perform topic modeling using LDA."""
        if len(texts) < 3:
            return {}
        
        try:
            # Prepare text for topic modeling
            processed_texts = [' '.join([word for word in word_tokenize(text.lower()) 
                                       if word.isalpha() and word not in self.stop_words]) 
                             for text in texts]
            
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
            
            # Perform LDA
            n_topics = min(5, len(texts) // 2)  # Adaptive number of topics
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
            lda.fit(tfidf_matrix)
            
            # Extract topics
            feature_names = self.vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words = [feature_names[i] for i in topic.argsort()[-10:]]
                topics.append({
                    'topic_id': topic_idx,
                    'top_words': top_words,
                    'weight': topic.max()
                })
            
            return {
                'n_topics': n_topics,
                'topics': topics,
                'topic_coherence': lda.score(tfidf_matrix)
            }
            
        except Exception as e:
            logger.error(f"Topic modeling failed: {e}")
            return {}
    
    def _create_behavioral_clusters(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create behavioral clusters from user data."""
        activities = user_data.get('posts', []) + user_data.get('comments', [])
        
        if not activities:
            return {}
        
        # Extract behavioral features
        features = []
        for activity in activities:
            feature_vector = [
                activity.get('score', 0),
                len(activity.get('body', '')),
                activity.get('num_comments', 0) if 'num_comments' in activity else 0,
                1 if activity.get('is_self', False) else 0
            ]
            features.append(feature_vector)
        
        if len(features) < 2:
            return {}
        
        try:
            # Perform clustering
            n_clusters = min(3, len(features) // 2)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(features)
            
            # Analyze clusters
            cluster_analysis = []
            for i in range(n_clusters):
                cluster_activities = [act for act, cluster in zip(activities, clusters) if cluster == i]
                cluster_analysis.append({
                    'cluster_id': i,
                    'size': len(cluster_activities),
                    'avg_score': np.mean([act.get('score', 0) for act in cluster_activities]),
                    'avg_length': np.mean([len(act.get('body', '')) for act in cluster_activities])
                })
            
            return {
                'n_clusters': n_clusters,
                'clusters': cluster_analysis,
                'cluster_labels': clusters.tolist()
            }
            
        except Exception as e:
            logger.error(f"Behavioral clustering failed: {e}")
            return {}
    
    def _estimate_mbti_type(self, texts: List[str]) -> Dict[str, Any]:
        """Estimate MBTI personality type from text analysis."""
        if not texts:
            return {}
        
        all_text = ' '.join(texts).lower()
        
        # MBTI indicators (simplified)
        mbti_indicators = {
            'E': ['social', 'people', 'group', 'party', 'friends', 'outgoing'],
            'I': ['alone', 'quiet', 'private', 'solitary', 'introvert', 'personal'],
            'S': ['practical', 'detail', 'fact', 'concrete', 'specific', 'realistic'],
            'N': ['creative', 'imagination', 'abstract', 'theory', 'possibility', 'vision'],
            'T': ['logic', 'analysis', 'reason', 'objective', 'factual', 'systematic'],
            'F': ['feel', 'emotion', 'value', 'relationship', 'harmony', 'compassion'],
            'J': ['plan', 'organize', 'structure', 'decide', 'control', 'schedule'],
            'P': ['flexible', 'spontaneous', 'open', 'explore', 'adapt', 'curious']
        }
        
        # Count indicators
        type_scores = {}
        for mbti_type, indicators in mbti_indicators.items():
            count = sum(1 for indicator in indicators if indicator in all_text)
            type_scores[mbti_type] = count
        
        # Determine type
        e_i = 'E' if type_scores.get('E', 0) > type_scores.get('I', 0) else 'I'
        s_n = 'S' if type_scores.get('S', 0) > type_scores.get('N', 0) else 'N'
        t_f = 'T' if type_scores.get('T', 0) > type_scores.get('F', 0) else 'F'
        j_p = 'J' if type_scores.get('J', 0) > type_scores.get('P', 0) else 'P'
        
        mbti_type = f"{e_i}{s_n}{t_f}{j_p}"
        
        # MBTI type descriptions
        mbti_descriptions = {
            'INTJ': 'The Architect - Imaginative and strategic thinkers',
            'INTP': 'The Logician - Innovative inventors with an unquenchable thirst for knowledge',
            'ENTJ': 'The Commander - Bold, imaginative and strong-willed leaders',
            'ENTP': 'The Debater - Smart and curious thinkers who cannot resist an intellectual challenge',
            'INFJ': 'The Advocate - Quiet and mystical, yet very inspiring and tireless idealists',
            'INFP': 'The Mediator - Poetic, kind and altruistic people, always eager to help a good cause',
            'ENFJ': 'The Protagonist - Charismatic and inspiring leaders, able to mesmerize their listeners',
            'ENFP': 'The Campaigner - Enthusiastic, creative and sociable free spirits',
            'ISTJ': 'The Logistician - Practical and fact-minded individuals, whose reliability cannot be doubted',
            'ISFJ': 'The Defender - Very dedicated and warm protectors, always ready to defend their loved ones',
            'ESTJ': 'The Executive - Excellent administrators, unsurpassed at managing things or people',
            'ESFJ': 'The Consul - Extraordinarily caring, social and popular people',
            'ISTP': 'The Virtuoso - Bold and practical experimenters, masters of all kinds of tools',
            'ISFP': 'The Adventurer - Flexible and charming artists, always ready to explore and experience something new',
            'ESTP': 'The Entrepreneur - Smart, energetic and very perceptive people',
            'ESFP': 'The Entertainer - Spontaneous, energetic and enthusiastic entertainers'
        }
        
        return {
            'type': mbti_type,
            'description': mbti_descriptions.get(mbti_type, 'Unknown type'),
            'scores': type_scores,
            'confidence': self._calculate_mbti_confidence(type_scores)
        }
    
    def _calculate_mbti_confidence(self, type_scores: Dict[str, int]) -> float:
        """Calculate confidence in MBTI assessment."""
        if not type_scores:
            return 0.0
        
        # Calculate how distinct the preferences are
        e_i_diff = abs(type_scores.get('E', 0) - type_scores.get('I', 0))
        s_n_diff = abs(type_scores.get('S', 0) - type_scores.get('N', 0))
        t_f_diff = abs(type_scores.get('T', 0) - type_scores.get('F', 0))
        j_p_diff = abs(type_scores.get('J', 0) - type_scores.get('P', 0))
        
        # Average difference indicates confidence
        avg_diff = (e_i_diff + s_n_diff + t_f_diff + j_p_diff) / 4
        confidence = min(avg_diff / 5, 1.0)  # Normalize to 0-1
        
        return confidence
    
    def _calculate_confidence_scores(self, analysis_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for each analysis component."""
        confidence_scores = {}
        
        # Text statistics confidence
        text_stats = analysis_results.get('text_statistics', {})
        if text_stats:
            confidence_scores['text_statistics'] = min(len(text_stats) / 10, 1.0)
        
        # Sentiment analysis confidence
        sentiment = analysis_results.get('sentiment_analysis', {})
        if sentiment:
            confidence_scores['sentiment_analysis'] = sentiment.get('confidence', 0.5)
        
        # Personality traits confidence
        personality = analysis_results.get('personality_traits', {})
        if personality:
            confidence_scores['personality_traits'] = personality.get('confidence', 0.5)
        
        # Interests confidence
        interests = analysis_results.get('interests', {})
        if interests:
            confidence_scores['interests'] = min(interests.get('interest_diversity', 0) / 5, 1.0)
        
        # Writing style confidence
        writing_style = analysis_results.get('writing_style', {})
        if writing_style:
            confidence_scores['writing_style'] = 0.8  # Generally reliable
        
        # Activity patterns confidence
        activity_patterns = analysis_results.get('activity_patterns', {})
        if activity_patterns:
            confidence_scores['activity_patterns'] = min(len(activity_patterns) / 5, 1.0)
        
        # Community engagement confidence
        community_engagement = analysis_results.get('community_engagement', {})
        if community_engagement:
            confidence_scores['community_engagement'] = 0.9  # Based on concrete data
        
        # Topic modeling confidence
        topic_modeling = analysis_results.get('topic_modeling', {})
        if topic_modeling:
            confidence_scores['topic_modeling'] = min(topic_modeling.get('n_topics', 0) / 3, 1.0)
        
        # MBTI confidence
        mbti = analysis_results.get('mbti_estimation', {})
        if mbti:
            confidence_scores['mbti_estimation'] = mbti.get('confidence', 0.5)
        
        return confidence_scores
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """Return empty analysis result structure."""
        return {
            'text_statistics': {},
            'sentiment_analysis': {},
            'personality_traits': {},
            'interests': {},
            'writing_style': {},
            'activity_patterns': {},
            'community_engagement': {},
            'topic_modeling': {},
            'behavioral_clusters': {},
            'mbti_estimation': {},
            'confidence_scores': {}
        } 