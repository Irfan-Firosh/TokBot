import cv2
import numpy as np
import re
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
from helpers.video.videoEditor import VideoCompiler
import os
import dotenv
from moviepy.editor import VideoFileClip, VideoClip

dotenv.load_dotenv()

def draw_rounded_rectangle(draw, bbox, radius, fill):
    x1, y1, x2, y2 = bbox
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)

class SubtitleClip:
    def __init__(self, text: str, start: float, end: float):
        self.text = text
        self.start = start
        self.end = end

def parse_srt_time(time_str: str) -> float:
    time_part, ms_part = time_str.strip().split(',')
    h, m, s = map(float, time_part.split(':'))
    return h * 3600 + m * 60 + s + float(ms_part) / 1000

def load_srt(file_path: str) -> List[SubtitleClip]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        subtitles = []
        for block in re.split(r'\n\n', content.strip()):
            lines = block.split('\n')
            if len(lines) < 3:
                continue
            
            try:
                start_str, end_str = lines[1].split('-->')
                start = parse_srt_time(start_str)
                end = parse_srt_time(end_str)
                text = re.sub(r'<[^>]+>|[.\[\]:;()\-\n]', '', ' '.join(lines[2:]).strip())
                text = text.lower()
                
                if text:
                    subtitles.append(SubtitleClip(text, start, end))
            except:
                continue
        
        return subtitles
    except:
        return []

def group_subtitles(subs: List[SubtitleClip], max_words=8, max_gap=1.0) -> List[SubtitleClip]:
    if not subs:
        return []
    
    grouped = []
    current = [subs[0]]
    word_count = len(subs[0].text.split())
    
    for sub in subs[1:]:
        gap = sub.start - current[-1].end
        new_words = len(sub.text.split())
        
        if word_count + new_words > max_words or gap > max_gap:
            text = ' '.join(s.text for s in current)
            grouped.append(SubtitleClip(text, current[0].start, current[-1].end))
            current = [sub]
            word_count = new_words
        else:
            current.append(sub)
            word_count += new_words
    
    if current:
        text = ' '.join(s.text for s in current)
        grouped.append(SubtitleClip(text, current[0].start, current[-1].end))
    
    return grouped

class SubtitleRenderer:
    def __init__(self, width: int, height: int, font_path: str):
        self.width = width
        self.height = height
        
        try:
            self.font = ImageFont.truetype(font_path, max(24, int(0.03 * height)))
        except:
            self.font = ImageFont.load_default()
    
    def render(self, text: str, center_position: bool = False) -> np.ndarray:
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        words = text.split()
        lines = []
        current_line = ""
        max_width = int(self.width * 0.9)
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if draw.textbbox((0, 0), test_line, font=self.font)[2] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        line_height = draw.textbbox((0, 0), "A", font=self.font)[3] * 1.2
        total_height = len(lines) * line_height
        
        if center_position:
            start_y = (self.height - total_height) // 2
        else:
            start_y = self.height - int(self.height * 0.12) - total_height - 200
        
        if lines:
            max_line_width = max(draw.textbbox((0, 0), line, font=self.font)[2] for line in lines)
            
            bbox_A = draw.textbbox((0, 0), "A", font=self.font)
            vertical_padding = (bbox_A[3] - bbox_A[1]) // 2
            horizontal_padding = (bbox_A[3] - bbox_A[1]) * 0.8
            
            box_width = max_line_width + 2 * horizontal_padding
            box_height = total_height + 2 * vertical_padding
            box_x = (self.width - box_width) // 2
            box_y = start_y - vertical_padding
            
            radius = 15
            draw_rounded_rectangle(draw, [box_x, box_y, box_x + box_width, box_y + box_height], radius, (0, 0, 0, 180))
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=self.font)
            x = (self.width - bbox[2]) // 2
            y = start_y + i * line_height
            
            draw.text((x, y), line, font=self.font, fill=(255, 255, 255))
        
        return np.array(img)

class SubtitleOverlay:
    def __init__(self, subs: List[SubtitleClip], width: int, height: int, font_path: str, initial_position_duration: float = 0.0):
        self.subs = sorted(subs, key=lambda x: x.start)
        self.renderer = SubtitleRenderer(width, height, font_path)
        self.initial_position_duration = initial_position_duration
        self.cache = {}
    
    def get_frame(self, t: float) -> Optional[np.ndarray]:
        for sub in self.subs:
            if sub.start <= t < sub.end:
                center_position = t >= self.initial_position_duration
                
                cache_key = f"{sub.text}_{center_position}"
                
                if cache_key not in self.cache:
                    self.cache[cache_key] = self.renderer.render(sub.text, center_position=center_position)
                
                return self.cache[cache_key]
        return None


def add_subtitles(file_path: str, output_path: str, max_words: int = 8, max_gap: float = 1.0):
    

    initial_position_duration = VideoCompiler.calculate_pic_duration(file_path)
    srt_path = f"{file_path}/audio.srt"
    font_path = os.getenv("SUBTITLE_FONT_PATH")

    video = VideoFileClip(f"{file_path}/compiled.mp4")
    subtitles = load_srt(srt_path)
    
    if not subtitles:
        print("No subtitles found")
        return
    
    grouped_subs = group_subtitles(subtitles, max_words=max_words, max_gap=max_gap)
    overlay = SubtitleOverlay(grouped_subs, video.w, video.h, font_path, initial_position_duration)
    
    def make_frame_with_subtitles(t):
        video_frame = video.get_frame(t)
        
        subtitle_frame = overlay.get_frame(t)
        
        if subtitle_frame is not None:
            if video_frame.shape[2] == 3:
                video_rgba = np.zeros((video.h, video.w, 4), dtype=np.uint8)
                video_rgba[:, :, :3] = video_frame
                video_rgba[:, :, 3] = 255
            else:
                video_rgba = video_frame
            
            alpha = subtitle_frame[:, :, 3:4] / 255.0
            result = video_rgba[:, :, :3] * (1 - alpha) + subtitle_frame[:, :, :3] * alpha
            return result.astype(np.uint8)
        
        return video_frame
    
    final_video = VideoClip(make_frame=make_frame_with_subtitles, duration=video.duration)
    
    if video.audio is not None:
        final_video = final_video.set_audio(video.audio)
    
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=video.fps)
    
    video.close()
    final_video.close()

if __name__ == "__main__":
    video_file = "output-1mhu024"
    subtitle_file = "/Users/irfanfirosh/Documents/Personal projects/TokBot/output-1mfyuzf/audio.srt"
    font_file = os.getenv("SUBTITLE_FONT_PATH")
    output_file = "output/compiled_with_subtitles.mp4"
    
    # Example: subtitles in current position for first 10 seconds, then centered for rest of video
    add_subtitles(video_file, output_file, max_words=5, max_gap=0.5)