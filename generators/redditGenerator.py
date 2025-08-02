import os
import sys

# Add the project root to Python path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from helpers.redditFetcher import RedditPostExtractor
from helpers.formatRedditpost import ImageGenerator
from helpers.sheetsLogger import SheetsLogger
from helpers.audioHandler import VoiceGenerator
import tqdm

VIRAL_POST_LIMIT = int(os.getenv("VIRAL_POST_LIMIT", "25"))
VIRAL_MIN_SCORE = int(os.getenv("VIRAL_MIN_SCORE", "100"))
VIRAL_MIN_RATIO = float(os.getenv("VIRAL_MIN_RATIO", "0.8"))
VIRAL_MIN_COMMENTS = int(os.getenv("VIRAL_MIN_COMMENTS", "10"))
VIRAL_TIME_FILTER = os.getenv("VIRAL_TIME_FILTER", "day")
VIRAL_MIN_BODY_LENGTH = int(os.getenv("VIRAL_MIN_BODY_LENGTH", "100"))
VIRAL_MAX_BODY_LENGTH = int(os.getenv("VIRAL_MAX_BODY_LENGTH", "1000"))

STORYTELLING_SUBREDDITS = list(os.getenv("STORYTELLING_SUBREDDITS", "tifu,AmItheAsshole,relationship_advice,MaliciousCompliance,entitledparents").split(","))


class RedditGenerator:
    def __init__(self):
        self.reddit_fetcher = RedditPostExtractor()
        self.image_generator = ImageGenerator()
        self.sheets_logger = SheetsLogger()
        self.voice_generator = VoiceGenerator()
    
    def fetch_reddit_posts(self):
        for subreddit in tqdm.tqdm(STORYTELLING_SUBREDDITS):
            posts = self.reddit_fetcher.get_top_posts_by_rating(subreddit, VIRAL_POST_LIMIT, VIRAL_MIN_SCORE, VIRAL_MIN_RATIO, VIRAL_MIN_COMMENTS, VIRAL_MIN_BODY_LENGTH, VIRAL_MAX_BODY_LENGTH)
            for post in posts:
                self.sheets_logger.append_row(post["id"], post["title"], post["url"], post["score"])
                self.image_generator.add_text_to_image(post["subreddit"], post["title"], f"output-{post['id']}/reddit.png")
                self.voice_generator.generate_audio(post["selftext"], f"output-{post['id']}/audio.wav")