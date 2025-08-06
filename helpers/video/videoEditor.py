from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip
import wave
from helpers.video.footageFetcher import YtClipFetcher
import math
import os
from typing import Optional

class VideoCompiler:
    def __init__(self, input_file_path: str, output_path: str):
        self.input_file_path = input_file_path
        self.output_path = output_path

    def compile_video(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        
        try:
            duration = self.calculate_pic_duration(self.input_file_path)
        except Exception as e:
            duration = 3
        
        clean_path = self.input_file_path.rstrip('/')
        video = VideoFileClip(f'{clean_path}/footage.mp4')
        title = ImageClip(f'{clean_path}/reddit.png').set_start(0).set_duration(duration).set_pos(("center","center"))
        audio = AudioFileClip(f'{clean_path}/audio.wav')
        final_video = CompositeVideoClip([video, title])
        final_video = final_video.set_audio(audio)
        final_video.write_videofile(self.output_path)
    
    def get_wav_duration(self):
        clean_path = self.input_file_path.rstrip('/')
        with wave.open(f'{clean_path}/audio.wav', 'rb') as audio_file:
            frames = audio_file.getnframes()
            rate = audio_file.getframerate()
            duration = frames / float(rate)
            return int(math.ceil(duration))
    
    def fetch_footage(self):
        # Ensure input_file_path doesn't end with slash to avoid double slashes
        clean_path = self.input_file_path.rstrip('/')
        output_path = f'{clean_path}/footage.mp4'
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        fetcher = YtClipFetcher(output_path)
        fetcher.fetch_clip(tiktok_crop=True, clip_duration=self.get_wav_duration())

    @staticmethod
    def calculate_pic_duration(input_file_path: str):
        clean_path = input_file_path.rstrip('/')
        with open(f"{clean_path}/title.txt", "r") as f:
            title = f.read()
        words = len(title.split())
        return min(round(words * 0.25), 10.0)
    
if __name__ == "__main__":
    video_compiler = VideoCompiler(
        input_file_path="/Users/irfanfirosh/Documents/Personal projects/TokBot/output-1mfyuzf",
        output_path="output/compiled.mp4"
    )
    video_compiler.fetch_footage()
    video_compiler.compile_video()