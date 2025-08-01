# Reddit Post Extractor

A Python tool to extract and filter Reddit posts based on various rating criteria including score, upvote ratio, and comment count.

## Features

- **Authentication**: Secure Reddit API authentication using client credentials
- **Flexible Filtering**: Filter posts by score, upvote ratio, and comment count
- **Multiple Time Filters**: Fetch posts from different time periods (hour, day, week, month, year, all)
- **Comprehensive Post Data**: Extract detailed post information including metadata
- **Easy to Use**: Simple class-based interface with clear documentation

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the details:
   - **Name**: Your app name (e.g., "RedditPostExtractor")
   - **Type**: Select "script"
   - **Description**: Optional description
   - **About URL**: Can be left blank
   - **Redirect URI**: Use `http://localhost:8080`
4. After creating, note down the **Client ID** (under the app name) and **Client Secret**

### 3. Environment Configuration

Create a `.env` file in the project root with your Reddit API credentials:

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

## Usage

### Basic Usage

```python
from helpers.fetcher import RedditPostExtractor

# Initialize the extractor
extractor = RedditPostExtractor()

# Get high-quality posts from r/Python
posts = extractor.get_top_posts_by_rating(
    subreddit='Python',
    limit=10,
    min_score=50,
    min_ratio=0.85,
    min_comments=5
)

# Print the results
extractor.print_posts_summary(posts)
```

### Advanced Filtering

```python
# Get all posts first
all_posts = extractor.get_posts('programming', limit=25)

# Apply custom filters
high_score_posts = extractor.filter_posts_by_score(all_posts, min_score=100)
viral_posts = extractor.filter_posts_by_ratio(all_posts, min_ratio=0.9)
active_posts = extractor.filter_posts_by_comments(all_posts, min_comments=20)
```

### Running the Example

```bash
python main.py
```

## API Reference

### RedditPostExtractor Class

#### Methods

- `get_posts(subreddit, limit=25, time_filter='day')`: Fetch posts from a subreddit
- `get_top_posts_by_rating(subreddit, limit=25, min_score=100, min_ratio=0.8, min_comments=10)`: Get posts with comprehensive filtering
- `filter_posts_by_score(posts, min_score=0, max_score=None)`: Filter by post score
- `filter_posts_by_ratio(posts, min_ratio=0.0)`: Filter by upvote ratio
- `filter_posts_by_comments(posts, min_comments=0)`: Filter by comment count
- `print_posts_summary(posts)`: Display formatted post information

#### Post Data Structure

Each post contains:
- `id`: Reddit post ID
- `title`: Post title
- `author`: Post author username
- `score`: Net score (upvotes - downvotes)
- `upvote_ratio`: Percentage of upvotes (0.0 to 1.0)
- `num_comments`: Number of comments
- `url`: Original post URL
- `permalink`: Reddit permalink
- `created_utc`: Post creation timestamp
- `subreddit`: Subreddit name
- `is_self`: Whether it's a text post
- `selftext`: Post text content
- `domain`: Domain of linked content
- `over_18`: NSFW flag
- `spoiler`: Spoiler flag
- `stickied`: Whether post is stickied

## Examples

### Get Viral Posts
```python
viral_posts = extractor.get_top_posts_by_rating(
    subreddit='technology',
    limit=15,
    min_score=1000,
    min_ratio=0.9,
    min_comments=20
)
```

### Get Recent Quality Posts
```python
recent_posts = extractor.get_posts('Python', limit=10, time_filter='week')
quality_posts = extractor.filter_posts_by_score(recent_posts, min_score=25)
```

## Error Handling

The extractor includes comprehensive error handling for:
- Missing environment variables
- Authentication failures
- API request errors
- Invalid parameters

## Rate Limiting

Reddit API has rate limits. The extractor respects these limits and will throw appropriate exceptions if limits are exceeded.

## License

This project is open source and available under the MIT License. # TokBot
