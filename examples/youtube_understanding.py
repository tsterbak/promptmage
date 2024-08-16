from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from promptmage import PromptMage, Prompt, MageResult
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


@mage.step(name="get-transcript", pass_through_inputs=["question"], initial=True)
def get_transcript(video_id: str, question: str) -> str:
    """Get the transcript of a YouTube video.

    Uses the YouTube API to get the transcript of a video with youtube-transcript-api.
    """
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["de"])
    transcript_text = TextFormatter().format_transcript(transcript)
    return MageResult(
        next_step=["create-outline", "extract-facts"], transcript=transcript_text
    )


@mage.step(name="create-outline", prompt_name="create-outline")
def create_outline(transcript: str, prompt: Prompt) -> str:
    """Create an outline from the transcript of a YouTube video."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt.system},
            {"role": "user", "content": prompt.user.format(transcript=transcript)},
        ],
    )
    return MageResult(
        next_step="answer-question", outline=response.choices[0].message.content
    )


@mage.step(name="extract-facts", prompt_name="extract-facts")
def extract_facts(transcript: str, prompt: Prompt) -> str:
    """Extract facts from the transcript of a YouTube video."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt.system},
            {"role": "user", "content": prompt.user.format(transcript=transcript)},
        ],
    )
    return MageResult(
        next_step="answer-question",
        facts=response.choices[0].message.content,
        question="What is the video about?",
    )


@mage.step(
    name="answer-question",
    prompt_name="answer-question",
    depends_on=["create-outline", "extract-facts"],
)
def answer_question(outline: str, facts: str, question: str, prompt: Prompt) -> str:
    """Answer a question based on the outline of a YouTube video."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(
                    outline=outline, facts=facts, question=question
                ),
            },
        ],
    )
    return MageResult(answer=response.choices[0].message.content)
