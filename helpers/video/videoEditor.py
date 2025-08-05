from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
import wave
from helpers.video.footageFetcher import YtClipFetcher
import math
import os

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
        
        video = VideoFileClip(f'{self.input_file_path}/footage.mp4')
        title = ImageClip(f'{self.input_file_path}/reddit.png').set_start(0).set_duration(duration).set_pos(("center","center"))
        audio = AudioFileClip(f'{self.input_file_path}/audio.wav')
        final_video = CompositeVideoClip([video, title])
        final_video = final_video.set_audio(audio)
        final_video.write_videofile(self.output_path)
    
    def get_wav_duration(self):
        with wave.open(f'{self.input_file_path}/audio.wav', 'rb') as audio_file:
            frames = audio_file.getnframes()
            rate = audio_file.getframerate()
            duration = frames / float(rate)
            return int(math.ceil(duration))
    
    def fetch_footage(self):
        url="https://www.youtube.com/watch?v=u7kdVe8q5zs&t=5s&pp=ygUnbWluZWNyYWZ0IHBhcmtvdXIgZ2FtZXBsYXkgbm8gY29weXJpZ2h0"
        fetcher = YtClipFetcher(url, f'{self.input_file_path}/footage.mp4')
        fetcher.fetch_clip(tiktok_crop=True, clip_duration=self.get_wav_duration())

    @staticmethod
    def calculate_pic_duration(input_file_path: str):
        with open(f"{input_file_path}/title.txt", "r") as f:
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