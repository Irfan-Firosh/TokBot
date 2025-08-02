import ffmpeg
import yt_dlp


class YtClipFetcher:
    def __init__(self, url: str, start_time: str, end_time: str, output_path: str):
        self.url = url
        self.start_time = start_time
        self.end_time = end_time
        self.output_path = output_path
        self.video_stream_url = None

    def fetch_stream_url(self):
        ydl_opts = {
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            video = info['entries'][0] if 'entries' in info else info
            self.video_stream_url = video['url']

    def fetch_clip(self, tiktok_crop: bool = False):
        if not self.video_stream_url:
            self.fetch_stream_url()
        start_time = self.time_to_seconds(self.start_time)
        duration = self.time_to_seconds(self.end_time) - start_time
        stream = ffmpeg.input(self.video_stream_url, ss=start_time)
        if tiktok_crop:
            filter = (
                "scale='if(lt(iw,1080),1080,iw)':'if(lt(ih,1920),1920,ih)',"
                "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,"
                "eq=brightness=-0.1:contrast=0.9"
            )
            stream = stream.output(
                self.output_path, 
                vf=filter, 
                t=duration,
                **{'c:v': 'libx264', 'preset': 'fast', 'crf': '18', 'y': None, 'an': None}
                )
        else:
            stream = stream.output(
                self.output_path, 
                vf='scale=1080:1920', 
                t=duration,
                **{'c:v': 'libx264', 'preset': 'fast', 'crf': '18', 'y': None, 'an': None}
                )
        stream.run(quiet=False)
    
    @staticmethod
    def time_to_seconds(time_str):
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

if __name__ == "__main__":  
    url="https://www.youtube.com/watch?v=u7kdVe8q5zs&pp=ygURbWluZWNyYWZ0IHBhcmtvdXLSBwkJxwkBhyohjO8%3D"
    start_time="00:00:15"
    end_time="00:00:25"
    output_path="demo.mp4"
    fetcher = YtClipFetcher(url, start_time, end_time, output_path)
    fetcher.fetch_clip(tiktok_crop=True)
