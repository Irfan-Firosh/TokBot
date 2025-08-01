"""
Generate audio and subtitles from transcript.
"""

import os
import requests
import json
from sseclient import SSEClient
import base64
import subprocess

class VoiceGenerator:
    def __init__(self):
        self.api_key = os.getenv("CARTESIA_API_KEY")
        self.voice_id = os.getenv("CARTESIA_VOICE_ID")
        self.base_url = "https://api.cartesia.ai"
        
        if not self.api_key:
            raise ValueError("CARTESIA_API_KEY environment variable is required")
        if not self.voice_id:
            raise ValueError("CARTESIA_VOICE_ID environment variable is required")

    def generate_audio(self, transcript: str, output_path: str = "output/audio.wav"):
        """
        Generate audio from transcript using Cartesia TTS API.
        
        Args:
            transcript: Text to convert to speech
            output_path: Path to save the audio file
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Cartesia-Version": "2025-04-16"
        }
        
        payload = {
            "model_id": "sonic-2",
            "transcript": transcript,
            "voice": {
                "mode": "id",
                "id": self.voice_id
            },
            "output_format": {
                "container": "raw",
                "encoding": "pcm_s16le",
                "sample_rate": 44100
            },
            "language": "en",
            "add_timestamps": True
        }
        
        response = requests.post(
            f"{self.base_url}/tts/sse",
            headers=headers,
            json=payload,
            stream=True
        )
        
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        
        client = SSEClient(response)
        audio_chunks = []
        timestamps = []
        
        for event in client.events():
            if event.event == "timestamps":
                data = json.loads(event.data)
                if "word_timestamps" in data:
                    timestamps.append(data["word_timestamps"])
                    
            
            elif event.event == "chunk":
                data = json.loads(event.data)
                if "data" in data:
                    audio_data = base64.b64decode(data["data"])
                    audio_chunks.append(audio_data)
            
            elif event.event == "done":
                break
        
        if audio_chunks:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            tmp_raw_path = output_path.replace(".wav", ".pcm")
            with open(tmp_raw_path, 'wb') as f:
                f.write(b''.join(audio_chunks))

            subprocess.run([
                "ffmpeg", "-y",
                "-f", "s16le",
                "-ar", "44100",
                "-ac", "1",
                "-i", tmp_raw_path,
                output_path
            ], check=True)

            os.remove(tmp_raw_path)
            print(f"Audio saved to: {output_path}")
            
            if timestamps:
                srt_path = output_path.replace(".wav", ".srt")
                self.generate_srt_from_timestamps(timestamps, srt_path)
            
            return output_path
        else:
            print("No audio data received")
            return None

    def generate_srt_from_timestamps(self, timestamps_list, output_path: str):
        """
        Convert timestamp data to SRT subtitle format.
        
        Args:
            timestamps_list: List of timestamp dictionaries from Cartesia API
            output_path: Path to save the .srt file
        """
        srt_content = []
        subtitle_index = 1
        
        for timestamp_data in timestamps_list:
            words = timestamp_data.get('words', [])
            starts = timestamp_data.get('start', [])
            ends = timestamp_data.get('end', [])
            
            phrase_length = 4
            for i in range(0, len(words), phrase_length):
                phrase_words = words[i:i + phrase_length]
                phrase_start = starts[i] if i < len(starts) else starts[-1]
                phrase_end = ends[min(i + phrase_length - 1, len(ends) - 1)]
                
                start_time = self._seconds_to_srt_time(phrase_start)
                end_time = self._seconds_to_srt_time(phrase_end)
                
                subtitle_text = " ".join(phrase_words)
                srt_entry = f"{subtitle_index}\n{start_time} --> {end_time}\n{subtitle_text}\n"
                srt_content.append(srt_entry)
                subtitle_index += 1
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))
        
        print(f"SRT file saved to: {output_path}")

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """
        Convert seconds to SRT time format (HH:MM:SS,mmm).
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    voice_generator = VoiceGenerator()
    transcript = """Each message object will have a ‘data’ attribute, as well as optional ‘event’, ‘id’, and ‘retry’ attributes.

Optional init parameters:

last_id: If provided, this parameter will be sent to the server to tell it to return only messages more recent than this ID.

retry: Number of milliseconds to wait after disconnects before attempting to reconnect. The server may change this by including a ‘retry’ line in a message. Retries are handled automatically by the SSEClient object.

You may also provide any additional keyword arguments supported by the Requests library, such as a ‘headers’ dict and a (username, password) tuple for ‘auth’."""
    voice_generator.generate_audio(transcript)