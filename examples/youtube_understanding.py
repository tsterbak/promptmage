from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from promptmage import PromptMage, Prompt
from promptmage.storage import (
    SQLitePromptBackend,
    SQLiteDataBackend,
    PromptStore,
    DataStore,
)


load_dotenv()


client = OpenAI()

# Setup the prompt store and data store
prompt_store = PromptStore(backend=SQLitePromptBackend())
data_store = DataStore(backend=SQLiteDataBackend())

# Create a new PromptMage instance
mage = PromptMage(
    name="youtube-understanding", prompt_store=prompt_store, data_store=data_store
)


@mage.step(name="get-transcript", depends_on=None, pass_through_inputs=["question"])
def get_transcript(video_id: str, question: str) -> str:
    """Get the transcript of a YouTube video.

    Uses the YouTube API to get the transcript of a video with youtube-transcript-api.
    """
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["de"])
    transcript_text = TextFormatter().format_transcript(transcript)
    return transcript_text


@mage.step(
    name="create-outline", prompt_name="create-outline", depends_on="get-transcript"
)
def create_outline(transcript: str, prompt: Prompt) -> str:
    """Create an outline from the transcript of a YouTube video."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": prompt.system},
            {"role": "user", "content": prompt.user.format(transcript=transcript)},
        ],
    )
    return response.choices[0].message.content


@mage.step(
    name="answer-question", prompt_name="answer-question", depends_on="create-outline"
)
def answer_question(outline: str, question: str, prompt: Prompt) -> str:
    """Answer a question based on the outline of a YouTube video."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(outline=outline, question=question),
            },
        ],
    )
    return response.choices[0].message.content
