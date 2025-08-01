# TokBot

A comprehensive Python tool for automating content creation and distribution. TokBot fetches viral Reddit posts, generates audio narration, creates formatted images, and uploads content to TikTok.

## Features

- **Reddit Content Extraction**: Fetch viral posts from multiple subreddits with advanced filtering
- **Audio Generation**: Convert Reddit post text to speech using Cartesia TTS API
- **Image Generation**: Create formatted images with Reddit post titles and subreddit names
- **TikTok Upload**: Automatically upload generated content to TikTok
- **Google Sheets Logging**: Track processed posts and their performance metrics
- **Flexible Configuration**: Environment-based configuration for all API keys and settings

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root with your API credentials:

```env
# Reddit API Configuration
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# TikTok Configuration
TIKTOK_SESSION_ID=your_tiktok_session_id_here

# Cartesia TTS API Configuration
CARTESIA_API_KEY=your_cartesia_api_key_here
CARTESIA_VOICE_ID=your_cartesia_voice_id_here

# Google Sheets Configuration (optional)
GOOGLE_SHEETS_CREDENTIALS_FILE=path_to_your_credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Content Generation Settings
VIRAL_POST_LIMIT=25
VIRAL_MIN_SCORE=100
VIRAL_MIN_RATIO=0.8
VIRAL_MIN_COMMENTS=10
VIRAL_TIME_FILTER=day
VIRAL_MIN_BODY_LENGTH=100
VIRAL_MAX_BODY_LENGTH=1000
STORYTELLING_SUBREDDITS=tifu,AmItheAsshole,relationship_advice,MaliciousCompliance,entitledparents
```

### 3. Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the details:
   - **Name**: Your app name (e.g., "TokBot")
   - **Type**: Select "script"
   - **Description**: Optional description
   - **About URL**: Can be left blank
   - **Redirect URI**: Use `http://localhost:8080`
4. After creating, note down the **Client ID** (under the app name) and **Client Secret**

### 4. TikTok Session ID Setup

To get your TikTok session ID:

1. Log in to your TikTok account
2. Go to https://www.tiktok.com/
3. Press the F12 key on your keyboard
4. Go to Application > Storage > Cookies
5. Find the value of the `sessionid` cookie
6. You should have something like this: `7a9f3c5d8f6e4b2a1c9d8e7f6a5b4c3d`

### 5. Cartesia TTS API Setup

1. Sign up for Cartesia TTS API at https://cartesia.ai/
2. Get your API key and voice ID
3. Add them to your `.env` file

## Usage

### Basic TikTok Upload

```python
from helpers.tiktokUploader import uploadVideo
import os
from dotenv import load_dotenv

load_dotenv()

uploadVideo(
    session_id=os.getenv("TIKTOK_SESSION_ID"),
    video_path="path/to/your/video.mp4",
    title="Your Video Title",
    tags=["tiktok", "funny", "viral"],
    schedule_time=0,  # 0 for immediate upload
)
```

### Reddit Content Generation

```python
from generators.redditGenerator import RedditGenerator

# Initialize the generator
generator = RedditGenerator()

# Fetch and process viral Reddit posts
generator.fetch_reddit_posts()
```

### Running the Main Application

```bash
python main.py
```

## Project Structure

```
TokBot/
├── generators/
│   ├── __init__.py
│   └── redditGenerator.py          # Main content generation logic
├── helpers/
│   ├── __init__.py
│   ├── audioHandler.py            # TTS audio generation
│   ├── formatRedditpost.py        # Image generation with templates
│   ├── redditFetcher.py           # Reddit API integration
│   ├── sheetsLogger.py            # Google Sheets logging
│   ├── tiktokUploader.py          # TikTok upload functionality
│   └── youtubeFetcher.py          # YouTube integration (future)
├── public/
│   ├── reddit-template.png        # Image template for Reddit posts
│   └── redditTemplate.png
├── main.py                        # Main application entry point
├── requirements.txt               # Python dependencies
└── README.md
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

### ImageGenerator Class

#### Methods

- `add_text_to_image(subreddit, post_title, output_path)`: Create formatted images with Reddit content
- `load_template()`: Load the template image for formatting

### VoiceGenerator Class

#### Methods

- `generate_audio(transcript, output_path)`: Convert text to speech using Cartesia TTS
- `generate_srt_from_timestamps(timestamps_list, output_path)`: Generate SRT subtitle files

### TikTok Uploader

#### Functions

- `uploadVideo(session_id, video, title, tags, schedule_time=0)`: Upload video to TikTok

## Configuration Options

### Content Filtering

- `VIRAL_POST_LIMIT`: Number of posts to fetch per subreddit
- `VIRAL_MIN_SCORE`: Minimum Reddit score threshold
- `VIRAL_MIN_RATIO`: Minimum upvote ratio (0.0 to 1.0)
- `VIRAL_MIN_COMMENTS`: Minimum comment count
- `VIRAL_TIME_FILTER`: Time period for posts ('hour', 'day', 'week', 'month', 'year', 'all')
- `VIRAL_MIN_BODY_LENGTH`: Minimum post text length
- `VIRAL_MAX_BODY_LENGTH`: Maximum post text length
- `STORYTELLING_SUBREDDITS`: Comma-separated list of subreddits to monitor

## Error Handling

The application includes comprehensive error handling for:
- Missing environment variables
- API authentication failures
- Network request errors
- File processing errors
- TikTok upload failures

## Rate Limiting

All APIs (Reddit, TikTok, Cartesia) have rate limits. The application respects these limits and includes appropriate error handling.

## Dependencies

- `requests>=2.31.0`: HTTP requests
- `python-dotenv>=1.0.0`: Environment variable management
- `Pillow>=10.0.0`: Image processing
- `sseclient-py>=1.7.2`: Server-sent events for TTS streaming

## License

This project is open source and available under the MIT License.
