import dotenv
from generators.redditGenerator import RedditGenerator
from helpers.reddit.formatRedditpost import ImageGenerator
from helpers.video.subtitleGenerator import add_subtitles
import os
dotenv.load_dotenv()

if __name__ == "__main__":
    redditGenerator = RedditGenerator()
    redditGenerator.fetch_reddit_posts()
