from dotenv import load_dotenv
from helpers.formatRedditpost import ImageGenerator

load_dotenv()


def main():
    imageGenerator = ImageGenerator()
    imageGenerator.add_text_to_image("askReddit", "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

if __name__ == "__main__":
    main()