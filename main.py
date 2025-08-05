import dotenv
from generators.redditGenerator import RedditGenerator
from helpers.reddit.formatRedditpost import ImageGenerator
from helpers.video.subtitleGenerator import add_subtitles
import os
dotenv.load_dotenv()

if __name__ == "__main__":
    video_file = "output-1mhu024"
    output_file = "output/compiled_with_subtitles.mp4"
    
    add_subtitles(video_file, output_file, max_words=5, max_gap=0.5)
