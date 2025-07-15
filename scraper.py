"""
Reddit Scraper Module
Handles data collection from Reddit using AsyncPRAW API with fallback to web scraping.
"""

import asyncio
import logging
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import asyncpraw
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class RedditScraper:
    """Reddit data scraper using AsyncPRAW API with fallback to web scraping."""
    
    def __init__(self):
        """Initialize the Reddit scraper with API credentials."""
        self.reddit = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Initialize AsyncPRAW if credentials are available
        self._init_asyncpraw()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.reddit:
            await self.reddit.close()
        self.session.close()
    
    def _init_asyncpraw(self):
        """Initialize AsyncPRAW Reddit client."""
        try:
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'PersonaAI/1.0 (by /u/PersonaAI_Bot)')
            
            if client_id and client_secret:
                self.reddit = asyncpraw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                logger.info("AsyncPRAW Reddit client initialized successfully")
            else:
                logger.warning("Reddit API credentials not found. Using web scraping fallback.")
                
        except Exception as e:
            logger.error(f"Failed to initialize AsyncPRAW: {e}")
            self.reddit = None
    
    async def scrape_user(self, username: str, max_posts: int = None, max_comments: int = None) -> Dict[str, Any]:
        """
        Scrape user data from Reddit.
        
        Args:
            username: Reddit username to scrape
            max_posts: Maximum number of posts to collect (None for all available)
            max_comments: Maximum number of comments to collect (None for all available)
            
        Returns:
            Dictionary containing user data
        """
        logger.info(f"Starting scrape for user: u/{username}")
        
        user_data = {
            'username': username,
            'posts': [],
            'comments': [],
            'user_info': {},
            'scraped_at': datetime.now().isoformat(),
            'source': 'asyncpraw' if self.reddit else 'web_scraping'
        }
        
        try:
            # Try AsyncPRAW first, fallback to web scraping
            if self.reddit:
                try:
                    user_data = await self._scrape_with_asyncpraw(username, max_posts, max_comments)
                    if user_data['posts'] or user_data['comments']:
                        logger.info(f"AsyncPRAW scraping successful: {len(user_data['posts'])} posts, {len(user_data['comments'])} comments")
                        return user_data
                    else:
                        logger.warning("AsyncPRAW returned no data, trying web scraping fallback")
                except Exception as e:
                    logger.error(f"AsyncPRAW scraping failed: {e}")
            
            # Fallback to web scraping
            user_data = await self._scrape_with_web(username, max_posts, max_comments)
            
            # If web scraping also fails, return minimal data
            if not user_data['posts'] and not user_data['comments']:
                logger.warning(f"No data collected for user {username} from any source")
                user_data['user_info'] = {
                    'name': username,
                    'created_utc': None,
                    'link_karma': 0,
                    'comment_karma': 0,
                    'is_gold': False,
                    'is_mod': False,
                    'has_verified_email': False
                }
            
            logger.info(f"Final scrape result: {len(user_data['posts'])} posts and {len(user_data['comments'])} comments")
            return user_data
            
        except Exception as e:
            logger.error(f"Error scraping user {username}: {e}")
            return user_data
    
    async def _scrape_with_asyncpraw(self, username: str, max_posts: int, max_comments: int) -> Dict[str, Any]:
        """Scrape user data using AsyncPRAW API."""
        user_data = {
            'username': username,
            'posts': [],
            'comments': [],
            'user_info': {},
            'scraped_at': datetime.now().isoformat(),
            'source': 'asyncpraw'
        }
        
        try:
            # Get user object and load it
            user = await self.reddit.redditor(username)
            await user.load()  # Load the user object to access attributes
            
            # Get user info
            user_data['user_info'] = {
                'name': user.name,
                'created_utc': user.created_utc,
                'link_karma': user.link_karma,
                'comment_karma': user.comment_karma,
                'is_gold': user.is_gold,
                'is_mod': user.is_mod,
                'has_verified_email': user.has_verified_email
            }
            
            # Scrape posts and comments concurrently
            posts_task = asyncio.create_task(self._scrape_posts_asyncpraw(user, max_posts))
            comments_task = asyncio.create_task(self._scrape_comments_asyncpraw(user, max_comments))
            
            user_data['posts'], user_data['comments'] = await asyncio.gather(
                posts_task, comments_task, return_exceptions=True
            )
            
            # Handle exceptions from gather
            if isinstance(user_data['posts'], Exception):
                logger.error(f"Posts scraping failed: {user_data['posts']}")
                user_data['posts'] = []
            if isinstance(user_data['comments'], Exception):
                logger.error(f"Comments scraping failed: {user_data['comments']}")
                user_data['comments'] = []
            
        except Exception as e:
            logger.error(f"AsyncPRAW scraping failed: {e}")
            raise
        
        return user_data
    
    async def _scrape_posts_asyncpraw(self, user, max_posts: int = None) -> List[Dict]:
        """Scrape user posts using AsyncPRAW."""
        posts = []
        
        try:
            # If max_posts is None, collect all available posts
            submissions = user.submissions.new(limit=max_posts) if max_posts else user.submissions.new()
            async for submission in submissions:
                try:
                    post_data = {
                        'id': submission.id,
                        'title': submission.title,
                        'body': submission.selftext,
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'created_utc': submission.created_utc,
                        'url': submission.url,
                        'permalink': submission.permalink,
                        'is_self': submission.is_self,
                        'over_18': submission.over_18,
                        'spoiler': submission.spoiler,
                        'stickied': submission.stickied,
                        'locked': submission.locked
                    }
                    posts.append(post_data)
                except Exception as e:
                    logger.warning(f"Error processing post {submission.id}: {e}")
                    continue
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error scraping posts with AsyncPRAW: {e}")
            raise
        
        return posts
    
    async def _scrape_comments_asyncpraw(self, user, max_comments: int = None) -> List[Dict]:
        """Scrape user comments using AsyncPRAW."""
        comments = []
        
        try:
            # If max_comments is None, collect all available comments
            comment_list = user.comments.new(limit=max_comments) if max_comments else user.comments.new()
            async for comment in comment_list:
                try:
                    comment_data = {
                        'id': comment.id,
                        'body': comment.body,
                        'subreddit': comment.subreddit.display_name,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'permalink': comment.permalink,
                        'parent_id': comment.parent_id,
                        'is_submitter': comment.is_submitter,
                        'distinguished': comment.distinguished,
                        'edited': comment.edited,
                        'gilded': comment.gilded,
                        'stickied': comment.stickied
                    }
                    comments.append(comment_data)
                except Exception as e:
                    logger.warning(f"Error processing comment {comment.id}: {e}")
                    continue
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error scraping comments with AsyncPRAW: {e}")
            raise
        
        return comments
    
    async def _scrape_with_web(self, username: str, max_posts: int = None, max_comments: int = None) -> Dict[str, Any]:
        """Scrape user data using web scraping."""
        user_data = {
            'username': username,
            'posts': [],
            'comments': [],
            'user_info': {},
            'scraped_at': datetime.now().isoformat(),
            'source': 'web_scraping'
        }
        
        try:
            # Scrape user profile page
            profile_url = f"https://www.reddit.com/user/{username}/"
            response = await self._make_request(profile_url)
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract basic user info
                user_data['user_info'] = self._extract_user_info_web(soup, username)
                
                # Scrape posts and comments from profile
                posts_task = asyncio.create_task(
                    self._scrape_posts_web(username, max_posts)
                )
                comments_task = asyncio.create_task(
                    self._scrape_comments_web(username, max_comments)
                )
                
                posts_result, comments_result = await asyncio.gather(
                    posts_task, comments_task, return_exceptions=True
                )
                
                # Handle exceptions from gather
                if isinstance(posts_result, Exception):
                    logger.error(f"Web posts scraping failed: {posts_result}")
                    user_data['posts'] = []
                else:
                    user_data['posts'] = posts_result
                
                if isinstance(comments_result, Exception):
                    logger.error(f"Web comments scraping failed: {comments_result}")
                    user_data['comments'] = []
                else:
                    user_data['comments'] = comments_result
            
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
        
        return user_data
    
    async def _scrape_posts_web(self, username: str, max_posts: int = None) -> List[Dict]:
        """Scrape user posts using web scraping from public HTML pages."""
        posts = []
        
        try:
            # Use Reddit's public HTML page for user posts
            url = f"https://www.reddit.com/user/{username}/submitted/"
            response = await self._make_request(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find post elements
                post_elements = soup.find_all('div', {'data-testid': 'post-container'})
                if not post_elements:
                    # Try alternative selectors
                    post_elements = soup.find_all('div', class_='Post')
                
                for i, post_element in enumerate(post_elements):
                    if max_posts and i >= max_posts:
                        break
                    
                    try:
                        # Extract post title
                        title_element = post_element.find('h3') or post_element.find('a', {'data-testid': 'post-title'})
                        title = title_element.get_text().strip() if title_element else "No title"
                        
                        # Extract subreddit
                        subreddit_element = post_element.find('a', href=lambda x: x and '/r/' in x)
                        subreddit = subreddit_element.get_text().strip() if subreddit_element else "unknown"
                        
                        # Extract score
                        score_element = post_element.find('span', {'data-testid': 'post-vote-count'})
                        score = int(score_element.get_text().strip()) if score_element else 0
                        
                        # Extract post body (if self post)
                        body_element = post_element.find('div', {'data-testid': 'post-content'})
                        body = body_element.get_text().strip() if body_element else ""
                        
                        post_data = {
                            'id': f"web_post_{i}",
                            'title': title,
                            'body': body,
                            'subreddit': subreddit,
                            'score': score,
                            'upvote_ratio': 1.0,
                            'num_comments': 0,
                            'created_utc': datetime.now().timestamp(),
                            'url': f"https://www.reddit.com/user/{username}/submitted/",
                            'permalink': f"https://www.reddit.com/user/{username}/submitted/",
                            'is_self': len(body) > 0,
                            'over_18': False,
                            'spoiler': False,
                            'stickied': False,
                            'locked': False
                        }
                        posts.append(post_data)
                        
                    except Exception as e:
                        logger.warning(f"Error processing web post {i}: {e}")
                        continue
                
                logger.info(f"Web scraping collected {len(posts)} posts")
            
        except Exception as e:
            logger.error(f"Error scraping posts with web scraping: {e}")
        
        return posts
    
    async def _scrape_comments_web(self, username: str, max_comments: int = None) -> List[Dict]:
        """Scrape user comments using web scraping from public HTML pages."""
        comments = []
        
        try:
            # Use Reddit's public HTML page for user comments
            url = f"https://www.reddit.com/user/{username}/comments/"
            response = await self._make_request(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find comment elements
                comment_elements = soup.find_all('div', {'data-testid': 'comment'})
                if not comment_elements:
                    # Try alternative selectors
                    comment_elements = soup.find_all('div', class_='Comment')
                
                for i, comment_element in enumerate(comment_elements):
                    if max_comments and i >= max_comments:
                        break
                    
                    try:
                        # Extract comment body
                        body_element = comment_element.find('div', {'data-testid': 'comment-content'})
                        if not body_element:
                            body_element = comment_element.find('p') or comment_element.find('span')
                        
                        body = body_element.get_text().strip() if body_element else "No content"
                        
                        # Extract subreddit
                        subreddit_element = comment_element.find('a', href=lambda x: x and '/r/' in x)
                        subreddit = subreddit_element.get_text().strip() if subreddit_element else "unknown"
                        
                        # Extract score
                        score_element = comment_element.find('span', {'data-testid': 'comment-vote-count'})
                        score = int(score_element.get_text().strip()) if score_element else 0
                        
                        comment_data = {
                            'id': f"web_comment_{i}",
                            'body': body,
                            'subreddit': subreddit,
                            'score': score,
                            'created_utc': datetime.now().timestamp(),
                            'permalink': f"https://www.reddit.com/user/{username}/comments/",
                            'parent_id': None,
                            'link_id': None,
                            'is_submitter': False,
                            'distinguished': None,
                            'edited': False,
                            'gilded': 0
                        }
                        comments.append(comment_data)
                        
                    except Exception as e:
                        logger.warning(f"Error processing web comment {i}: {e}")
                        continue
                
                logger.info(f"Web scraping collected {len(comments)} comments")
            
        except Exception as e:
            logger.error(f"Error scraping comments with web scraping: {e}")
        
        return comments
    
    def _extract_user_info_web(self, soup: BeautifulSoup, username: str) -> Dict[str, Any]:
        """Extract user information from profile page."""
        user_info = {
            'name': username,
            'created_utc': None,
            'link_karma': 0,
            'comment_karma': 0,
            'is_gold': False,
            'is_mod': False,
            'has_verified_email': False
        }
        
        try:
            # Try to extract karma information
            karma_elements = soup.find_all('span', class_='karma')
            if karma_elements:
                for element in karma_elements:
                    text = element.get_text()
                    if 'post karma' in text.lower():
                        user_info['link_karma'] = int(''.join(filter(str.isdigit, text)))
                    elif 'comment karma' in text.lower():
                        user_info['comment_karma'] = int(''.join(filter(str.isdigit, text)))
            
            # Check for gold status
            gold_elements = soup.find_all('span', class_='gold')
            user_info['is_gold'] = len(gold_elements) > 0
            
        except Exception as e:
            logger.error(f"Error extracting user info: {e}")
        
        return user_info
    
    async def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with rate limiting and error handling."""
        try:
            # Rate limiting
            await asyncio.sleep(1)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def get_user_summary(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of scraped user data."""
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        
        summary = {
            'total_posts': len(posts),
            'total_comments': len(comments),
            'total_activity': len(posts) + len(comments),
            'avg_post_score': sum(p.get('score', 0) for p in posts) / max(len(posts), 1),
            'avg_comment_score': sum(c.get('score', 0) for c in comments) / max(len(comments), 1),
            'top_subreddits': self._get_top_subreddits(posts + comments),
            'activity_timeline': self._get_activity_timeline(posts + comments),
            'user_info': user_data.get('user_info', {})
        }
        
        return summary
    
    def _get_top_subreddits(self, activities: List[Dict]) -> List[Dict]:
        """Get top subreddits by activity."""
        subreddit_counts = {}
        
        for activity in activities:
            subreddit = activity.get('subreddit', 'unknown')
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        
        # Sort by count and return top 10
        sorted_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'subreddit': sub, 'count': count} for sub, count in sorted_subreddits[:10]]
    
    def _get_activity_timeline(self, activities: List[Dict]) -> Dict[str, int]:
        """Get activity timeline by month."""
        timeline = {}
        
        for activity in activities:
            created_utc = activity.get('created_utc')
            if created_utc:
                # Convert to datetime and get month
                dt = datetime.fromtimestamp(created_utc)
                month_key = dt.strftime('%Y-%m')
                timeline[month_key] = timeline.get(month_key, 0) + 1
        
        return timeline 