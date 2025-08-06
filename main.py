from generators.redditGenerator import RedditGenerator
import dotenv

dotenv.load_dotenv()

redditGenerator = RedditGenerator()
redditGenerator.upload_to_tiktok()