import os
import json
from dotenv import load_dotenv
from generators.redditGenerator import RedditGenerator
load_dotenv()


def main():
    reddit_generator = RedditGenerator()
    reddit_generator.fetch_reddit_posts()

if __name__ == "__main__":
    main()