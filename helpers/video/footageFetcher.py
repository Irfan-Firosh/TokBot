import yt_dlp
import ffmpeg
import random
from typing import Optional
import os
import time
import concurrent.futures

class YtClipFetcher:
    def __init__(self, output_path: str, url: Optional[str] = None):
        
        self.output_path = output_path
        self.video_stream_url = url
        self.video_duration = None
        self.footages = os.getenv("FOOTAGE_LINKS").split(",")


    def fetch_stream_url(self):
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'merge_output_format': 'mp4',
            'quiet': True
        }
        
        urls_to_try = [self.video_stream_url] if self.video_stream_url else []
        
        if self.footages:
            urls_to_try.extend(self.footages)
        
        seen = set()
        urls_to_try = [url for url in urls_to_try if not (url in seen or seen.add(url))]
        
        last_error = None
        
        for url in urls_to_try:
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:   
                    future = executor.submit(yt_dlp.YoutubeDL(ydl_opts).extract_info, url, download=False)
                    info = future.result(timeout=60)
                    video = info['entries'][0] if 'entries' in info else info
                    formats = video.get('formats', [])
                    candidates = [f for f in formats if f.get('ext') == 'mp4' and f.get('height') and f['height'] <= 720 and f.get('url')]

                    candidates.sort(key=lambda x: x['height'], reverse=True)

                if candidates:
                    self.video_stream_url = candidates[0]['url']
                else:
                    self.video_stream_url = video.get('url')
                self.video_duration = video.get('duration')
                return 
            except Exception as e:
                error_str = str(e)
                if "SABR streaming" in error_str or "missing a url" in error_str:
                    print(f"SABR streaming issue detected for {url}, trying next URL...")
                    continue
                else:
                    last_error = e
                    continue
        
        raise Exception(f"Failed to fetch footage from all available URLs. Last error: {str(last_error)}")

    def get_video_dimensions(self):
        try:
            probe = ffmpeg.probe(self.video_stream_url)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            width = int(video_info['width'])
            height = int(video_info['height'])
            return width, height
        except Exception as e:
            return 1920, 1080

    def fetch_clip(self, tiktok_crop: bool = False, clip_duration: Optional[int] = None, start_time: Optional[str] = None, end_time: Optional[str] = None):
        self.fetch_stream_url()
        
        if clip_duration and self.video_duration:
            start_time, end_time = self.dynamic_duration(clip_duration+1, self.video_duration)
            duration = clip_duration
        elif start_time and end_time:
            start_time = self.time_to_seconds(start_time)
            duration = self.time_to_seconds(end_time) - start_time + 1
        else:
            raise ValueError("Either clip_duration or start_time and end_time must be provided")
        
        last_error = None
        
        for attempt in range(5):
            try:
                stream = ffmpeg.input(self.video_stream_url, ss=start_time)

                if tiktok_crop:
                    filter_str = (
                        "crop='if(gt(iw/ih,9/16),ih*9/16,iw)':'if(gt(iw/ih,9/16),ih,iw*16/9)':"
                        "'(iw-if(gt(iw/ih,9/16),ih*9/16,iw))/2':'(ih-if(gt(iw/ih,9/16),ih,iw*16/9))/2',"
                        "scale=1080:1920"
                    )
            
                    stream = stream.output(
                        self.output_path, 
                        t=duration,
                        vf=filter_str,
                        **{
                            'c:v': 'libx264',
                            'crf': '18',
                            'preset': 'fast',
                            'format': 'mp4',
                            'y': None,
                            'an': None
                        }
                    )
                else:
                    stream = stream.output(
                        self.output_path, 
                        t=duration,
                        **{
                            'c:v': 'libx264', 
                            'qp': '0', 
                            'preset': 'fast', 
                            'crf': '18', 
                            'y': None, 
                            'an': None
                        }
                    )
                
                stream.run(quiet=True)
                return 
                
            except Exception as e:
                last_error = e
                
                if attempt < 4:
                    wait_time = 60 * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed to fetch clip after 5 attempts. Last error: {str(last_error)}")
                continue
        
        raise Exception(f"Failed to fetch clip after 5 attempts. Last error: {str(last_error)}")
    
    @staticmethod
    def time_to_seconds(time_str):
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    
    @staticmethod
    def dynamic_duration(clip_duration: int, video_duration: int):
        start_time_seconds = random.randint(0, video_duration - clip_duration)
        end_time_seconds = start_time_seconds + clip_duration
        return start_time_seconds, end_time_seconds
    
if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    fetcher = YtClipFetcher(output_path="test.mp4")
    fetcher.fetch_clip(clip_duration=10, tiktok_crop=True)