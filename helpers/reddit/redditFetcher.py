import os
import requests
from typing import List, Dict, Optional
from datetime import datetime
from helpers.uploaders.sheetsLogger import SheetsLogger

class RedditPostExtractor:
    """
    A class to extract and filter Reddit posts based on various criteria including rating scores.
    Supports authentication via Reddit API and provides methods to fetch posts from subreddits
    with customizable filtering options.
    """
    
    def __init__(self):
        """Initialize the Reddit API client with credentials from environment variables."""
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = 'RedditPostExtractor/1.0'
        self.sheetsLogger = SheetsLogger() 
        if not self.client_id or not self.client_secret:
            raise ValueError("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set in .env file")
        
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Reddit API using client credentials flow."""
        auth_url = 'https://www.reddit.com/api/v1/access_token'
        auth_data = {
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(
            auth_url,
            data=auth_data,
            auth=(self.client_id, self.client_secret),
            headers={'User-Agent': self.user_agent}
        )
        
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
        else:
            raise Exception(f"Authentication failed: {response.status_code}")
    
    def get_posts(self, subreddit: str, limit: int = 25, time_filter: str = 'day') -> List[Dict]:
        """
        Fetch posts from a specified subreddit with basic filtering.
        
        Args:
            subreddit: Name of the subreddit to fetch posts from
            limit: Maximum number of posts to fetch (default: 25)
            time_filter: Time period for posts ('hour', 'day', 'week', 'month', 'year', 'all')
        
        Returns:
            List of post dictionaries containing post data
        """
        if not self.access_token:
            self._authenticate()
        
        url = f'https://oauth.reddit.com/r/{subreddit}/top.json'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': self.user_agent
        }
        params = {
            'limit': limit,
            't': time_filter
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            posts = response.json()['data']['children']
            return [self._parse_post(post['data']) for post in posts]
        else:
            raise Exception(f"Failed to fetch posts: {response.status_code}")
    
    def filter_posts_by_score(self, posts: List[Dict], min_score: int = 0, max_score: Optional[int] = None) -> List[Dict]:
        """
        Filter posts based on their score (upvotes - downvotes).
        
        Args:
            posts: List of post dictionaries to filter
            min_score: Minimum score threshold (default: 0)
            max_score: Maximum score threshold (optional)
        
        Returns:
            Filtered list of posts meeting the score criteria
        """
        filtered_posts = []
        
        for post in posts:
            score = post.get('score', 0)
            if score >= min_score and (max_score is None or score <= max_score):
                filtered_posts.append(post)
        
        return filtered_posts
    
    def filter_posts_by_ratio(self, posts: List[Dict], min_ratio: float = 0.0) -> List[Dict]:
        """
        Filter posts based on upvote ratio (percentage of upvotes).
        
        Args:
            posts: List of post dictionaries to filter
            min_ratio: Minimum upvote ratio threshold (0.0 to 1.0)
        
        Returns:
            Filtered list of posts meeting the ratio criteria
        """
        filtered_posts = []
        
        for post in posts:
            upvote_ratio = post.get('upvote_ratio', 0.0)
            if upvote_ratio >= min_ratio:
                filtered_posts.append(post)
        
        return filtered_posts
    
    def filter_posts_by_comments(self, posts: List[Dict], min_comments: int = 0) -> List[Dict]:
        """
        Filter posts based on number of comments.
        
        Args:
            posts: List of post dictionaries to filter
            min_comments: Minimum number of comments required
        
        Returns:
            Filtered list of posts meeting the comment criteria
        """
        filtered_posts = []
        
        for post in posts:
            num_comments = post.get('num_comments', 0)
            if num_comments >= min_comments:
                filtered_posts.append(post)
        
        return filtered_posts
    
    def filter_posts_by_body_length(self, posts: List[Dict], min_body_length: int = 100, max_body_length: int = 1000) -> List[Dict]:
        """
        Filter posts based on the length of the post body (selftext).
        
        Args:
            posts: List of post dictionaries to filter
            min_body_length: Minimum number of characters in the post body
            max_body_length: Maximum number of characters in the post body
        Returns:
            Filtered list of posts meeting the body length criteria
        """
        filtered_posts = []
        
        for post in posts:
            # Get the body text (selftext for text posts, or empty string for link posts)
            body_text = post.get('selftext', '')
            body_length = len(body_text.strip())
            
            if body_length >= min_body_length and body_length <= max_body_length:
                filtered_posts.append(post)
        
        return filtered_posts
    
    def filter_posts_by_nsfw(self, posts: List[Dict], is_nsfw: bool = False) -> List[Dict]:
        """
        Filter posts based on whether they are NSFW.
        
        Args:
            posts: List of post dictionaries to filter
            is_nsfw: Whether to filter for NSFW posts   
        
        Returns:
            Filtered list of posts meeting the NSFW criteria
        """
        filtered_posts = []
        
        for post in posts:
            if post.get('over_18', False) == is_nsfw:
                filtered_posts.append(post)
        
        return filtered_posts
    
    def filter_used_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        Filter posts that have already been used.
        """
        used_post_ids = self.sheetsLogger.get_ids_set()
        return [post for post in posts if post.get('id') not in used_post_ids]  

    
    def get_top_posts_by_rating(self, subreddit: str, limit: int = 25, 
                               min_score: int = 100, min_ratio: float = 0.8,
                               min_comments: int = 10, min_body_length: int = 100, max_body_length: int = 1000) -> List[Dict]:
        """
        Get top posts from a subreddit with comprehensive rating filters.
        Fetches posts until we have enough that meet all criteria.
        
        Args:
            subreddit: Name of the subreddit to fetch posts from
            limit: Maximum number of posts to return (will fetch more to ensure we get enough)
            min_score: Minimum score threshold
            min_ratio: Minimum upvote ratio threshold
            min_comments: Minimum number of comments required
            min_body_length: Minimum number of characters in the post body
            max_body_length: Maximum number of characters in the post body  
        Returns:
            List of high-quality posts meeting all criteria
        """
        seen_ids = set()
        all_posts = []
        fetch_limit = min(limit * 3, 100)
        max_fetch_attempts = 5
        current_fetch = 0
        total_fetched = 0
        
        while len(all_posts) < limit and current_fetch < max_fetch_attempts:
            current_fetch += 1
            
            new_posts = self.get_posts(subreddit, fetch_limit)
            
            if not new_posts:
                break
            
            total_fetched += len(new_posts)
            
            filtered_posts = self.filter_posts_by_score(new_posts, min_score)
            filtered_posts = self.filter_posts_by_ratio(filtered_posts, min_ratio)
            filtered_posts = self.filter_posts_by_comments(filtered_posts, min_comments)
            filtered_posts = self.filter_posts_by_body_length(filtered_posts, min_body_length, max_body_length)
            filtered_posts = self.filter_posts_by_nsfw(filtered_posts, False)
            filtered_posts = self.filter_used_posts(filtered_posts)
            
            for post in filtered_posts:
                if post['id'] not in seen_ids:
                    seen_ids.add(post['id'])
                    all_posts.append(post)
            
            if len(all_posts) >= limit:
                break
            
            fetch_limit = min(int(fetch_limit * 1.5), 100)
        
        all_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
        result = all_posts[:limit]
        
        print(f"Fetched {total_fetched} total posts, filtered to {len(result)} posts meeting criteria")
        
        return result
    
    def _parse_post(self, post_data: Dict) -> Dict:
        """
        Parse raw Reddit post data into a standardized format.
        
        Args:
            post_data: Raw post data from Reddit API
        
        Returns:
            Standardized post dictionary with relevant fields
        """
        return {
            'id': post_data.get('id'),
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'score': post_data.get('score', 0),
            'upvote_ratio': post_data.get('upvote_ratio', 0.0),
            'num_comments': post_data.get('num_comments', 0),
            'url': post_data.get('url'),
            'permalink': f"https://reddit.com{post_data.get('permalink', '')}",
            'created_utc': datetime.fromtimestamp(post_data.get('created_utc', 0)),
            'subreddit': post_data.get('subreddit'),
            'is_self': post_data.get('is_self', False),
            'selftext': post_data.get('selftext', ''),
            'domain': post_data.get('domain'),
            'over_18': post_data.get('over_18', False),
            'spoiler': post_data.get('spoiler', False),
            'stickied': post_data.get('stickied', False)
        }
    
    def print_posts_summary(self, posts: List[Dict]):
        """
        Print a formatted summary of the filtered posts.
        
        Args:
            posts: List of post dictionaries to display
        """
        print(f"\nFound {len(posts)} posts meeting the criteria:\n")
        
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title']}")
            print(f"   Author: u/{post['author']}")
            print(f"   Score: {post['score']} | Ratio: {post['upvote_ratio']:.2f} | Comments: {post['num_comments']}")
            print(f"   URL: {post['permalink']}")
            print(f"   Created: {post['created_utc'].strftime('%Y-%m-%d %H:%M:%S')}")
            print()
