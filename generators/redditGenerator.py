import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from helpers.reddit.redditFetcher import RedditPostExtractor
from helpers.reddit.formatRedditpost import ImageGenerator
from helpers.uploaders.sheetsLogger import SheetsLogger
from helpers.video.audioHandler import VoiceGenerator
from helpers.video.videoEditor import VideoCompiler
import tqdm


class RedditGenerator:
    def __init__(self):
        self.reddit_fetcher = RedditPostExtractor()
        self.image_generator = ImageGenerator()
        self.sheets_logger = SheetsLogger()
        self.voice_generator = VoiceGenerator()
        self.STORYTELLING_SUBREDDITS = list(os.getenv("STORYTELLING_SUBREDDITS").split(","))
        self.VIRAL_POST_LIMIT = int(os.getenv("VIRAL_POST_LIMIT"))
        self.VIRAL_MIN_SCORE = int(os.getenv("VIRAL_MIN_SCORE"))
        self.VIRAL_MIN_RATIO = float(os.getenv("VIRAL_MIN_RATIO"))
        self.VIRAL_MIN_COMMENTS = int(os.getenv("VIRAL_MIN_COMMENTS"))
        self.VIRAL_TIME_FILTER = os.getenv("VIRAL_TIME_FILTER")
        self.VIRAL_MIN_BODY_LENGTH = int(os.getenv("VIRAL_MIN_BODY_LENGTH"))
        self.VIRAL_MAX_BODY_LENGTH = int(os.getenv("VIRAL_MAX_BODY_LENGTH"))

    def fetch_reddit_posts(self):
        for subreddit in tqdm.tqdm(self.STORYTELLING_SUBREDDITS):
            output_folders = [folder for folder in os.listdir(".") if folder.startswith("output-") and os.path.isdir(folder)]
            if len(output_folders) >= self.VIRAL_POST_LIMIT:
                print(f"Already have {len(output_folders)} posts, skipping fetch")
                break
            
            posts = self.reddit_fetcher.get_top_posts_by_rating(subreddit, self.VIRAL_POST_LIMIT - len(output_folders), self.VIRAL_MIN_SCORE, self.VIRAL_MIN_RATIO, self.VIRAL_MIN_COMMENTS, self.VIRAL_MIN_BODY_LENGTH, self.VIRAL_MAX_BODY_LENGTH)
            for post in posts:
                _, post_title = self.image_generator.add_text_to_image(post["subreddit"], post["title"], f"output-{post['id']}/reddit.png")
                self.voice_generator.generate_audio(post["selftext"], f"output-{post['id']}/audio.wav")
                with open(f"output-{post['id']}/title.txt", "w") as f:
                    f.write(post_title)
                self.sheets_logger.append_row(post["id"], post["title"], post["url"], post["score"])
                
        output_folders = [folder for folder in os.listdir(".") if folder.startswith("output-") and os.path.isdir(folder)]
        output_folders.sort()
        
        compiled_count = 0
        for folder in output_folders:
            if compiled_count >= self.VIRAL_POST_LIMIT:
                break
                
            folder_path = folder
            compiled_video_path = os.path.join(folder_path, "compiled.mp4")
            
            if not os.path.exists(compiled_video_path):
                try:
                    video_compiler = VideoCompiler(folder_path + "/", compiled_video_path)
                    video_compiler.fetch_footage()
                    video_compiler.compile_video()
                    compiled_count += 1
                except Exception as e:
                    print(f"Error compiling video for {folder}: {e}")
                    continue
            else:
                compiled_count += 1
        

        
        
