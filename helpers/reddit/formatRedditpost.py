from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, Optional

class ImageGenerator:
    def __init__(self, template_path: str = "public/redditTemplate.png"):
        """
        Initialize the image generator with a template.
        
        Args:
            template_path: Path to the template image
        """
        self.template_path = template_path
        self.template = None
        self.load_template()
    
    def load_template(self):
        """Load the template image."""
        try:
            self.template = Image.open(self.template_path)
        except Exception as e:
            raise Exception(f"Failed to load template image: {e}")
    
    def add_text_to_image(
        self, 
        subreddit: str, 
        post_title: str, 
        output_path: str = "output/reddit_post.png",
        subreddit_font_size: int = 40,
        title_font_size: int = 34,
        font_color: Tuple[int, int, int] = (0, 0, 0),
        subreddit_position: Optional[Tuple[int, int]] = None,
        title_position: Optional[Tuple[int, int]] = None
    ):
        """
        Add subreddit and post title text to the template image.
        
        Args:
            subreddit: Name of the subreddit
            post_title: Title of the reddit post
            output_path: Path to save the generated image
            font_size: Size of the font
            font_color: RGB color tuple for the text
            subreddit_position: Custom position for subreddit text (x, y)
            title_position: Custom position for title text (x, y)
        """
        if self.template is None:
            raise Exception("Template not loaded")
        
        img = self.template.copy()
        draw = ImageDraw.Draw(img)
        try:
            subreddit_font = ImageFont.truetype(os.getenv("SUBREDDIT_FONT_PATH"), subreddit_font_size)
            title_font = ImageFont.truetype(os.getenv("TITLE_FONT_PATH"), title_font_size)
        except:
            subreddit_font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        if subreddit_position is None:
            subreddit_x = 324
            subreddit_y = (745 + 804) // 2 - 20
            subreddit_position = (subreddit_x, subreddit_y)
        
        if title_position is None:
            title_x = 188 + 20
            title_y = 878
            title_position = (title_x, title_y)
        
        draw.text(subreddit_position, f"r/{subreddit}", font=subreddit_font, fill=font_color)
        
        title_max_width = 896 - 188 - 40
        
        self._draw_wrapped_text(draw, post_title, title_position, title_font, font_color, title_max_width)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        img.save(output_path)
        
        return output_path, post_title
    
    def _draw_wrapped_text(
        self, 
        draw: ImageDraw.Draw, 
        text: str, 
        position: Tuple[int, int], 
        font: ImageFont.FreeTypeFont, 
        color: Tuple[int, int, int], 
        max_width: int
    ):
        """
        Draw text with word wrapping.
        
        Args:
            draw: ImageDraw object
            text: Text to draw
            position: Starting position (x, y)
            font: Font to use
            color: Text color
            max_width: Maximum width for text wrapping
        """
        x, y = position
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width > max_width:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(" ".join(current_line))
        
        line_height = font.size + 5
        for line in lines:
            draw.text((x, y), line, font=font, fill=color)
            y += line_height
    
    def get_template_size(self) -> Tuple[int, int]:
        """Get the dimensions of the template image."""
        if self.template is None:
            raise Exception("Template not loaded")
        return self.template.size 