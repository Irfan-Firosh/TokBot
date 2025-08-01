from youtube_transcript_api import YouTubeTranscriptApi 
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from langchain_groq import ChatGroq
import os
from langchain_core.rate_limiters import InMemoryRateLimiter

class ChunkRating(BaseModel):
    chunk_id: int
    rating: int
    starting_rating: int


class YoutubeFetcher:
    def __init__(self, video_id: str, max_duration: int = 30, overlap_max: int = 5):
        self.yt = YouTubeTranscriptApi()
        self.video_id = video_id
        self.max_duration = max_duration
        self.overlap_max = overlap_max


    def fetch_transcript(self):
        transcript_list = self.yt.list(self.video_id)
        transcript = transcript_list.find_transcript(["en"])
        if transcript is None:
            raise Exception("No transcript found")
        return transcript.fetch()


    def chunk_by_duration(self):
        chunks = []
        duration = 0.0
        current_chunks = []
        overlap_chunks = []
        overlap_duration = 0.0
        chunk_id = 0

        for entry in self.fetch_transcript():
            duration += entry.duration
            current_chunks.append(entry)

            overlap_chunks.append(entry)
            overlap_duration += entry.duration
            while overlap_duration > self.overlap_max:
                overlap_duration -= overlap_chunks[0].duration
                overlap_chunks.pop(0)
            

            if duration >= self.max_duration:
                chunks.append([chunk_id, current_chunks, duration])
                current_chunks = overlap_chunks.copy()
                duration = overlap_duration
                chunk_id += 1

        if current_chunks and (not chunks or current_chunks != chunks[-1][0]):
            chunks.append([chunk_id, current_chunks, duration])

        return chunks
    
    def rate_chunks(self):
        llm = ChatGroq(
            model="llama3-70b-8192",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.8
        )

        structured_llm = llm.with_structured_output(ChunkRating)

        prompt = ChatPromptTemplate.from_messages([
            ("system", 
                """You are an expert content strategist. 
                    Rate the following transcript chunk on its potential to go viral as a YouTube Short.
                    - `rating`: How likely the chunk is to go viral based on content (1–10).
                - `starting_rating`: How good it would be as the first short in a series (1–10).
                Only provide these two scores as integers.
                The chunk is: {chunk_content}
                The duration is: {duration} seconds
                The overlap is: {overlap} seconds
                """),
            ("user", 
            "Transcript chunk:\n\n{chunk_content}\n\nDuration: {duration} seconds\nOverlap: {overlap} seconds")
        ])

        chunks = self.chunk_by_duration()
        chunk_responses = []

        for chunk_id, chunk_entries, duration in chunks:
            response = structured_llm.invoke(prompt.format(
                chunk_content=chunk_entries,
                duration=duration,
                overlap=self.overlap_max,
            ))
            response.chunk_id = chunk_id
            chunk_responses.append(response)

        

        return chunk_responses

    



