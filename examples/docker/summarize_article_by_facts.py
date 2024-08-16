from dotenv import load_dotenv
from openai import OpenAI

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
    name="fact-extraction", prompt_store=prompt_store, data_store=data_store
)


# Application code


@mage.step(name="extract", prompt_name="extract_facts", initial=True)
def extract_facts(article: str, prompt: Prompt) -> str:
    """Extract the facts as a bullet list from an article."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",  # "llama3:instruct",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(article=article),
            },
        ],
    )
    return MageResult(next_step="summarize", facts=response.choices[0].message.content)


@mage.step(name="summarize", prompt_name="summarize_facts")
def summarize_facts(facts: str, prompt: Prompt) -> str:
    """Summarize the given facts as a single sentence."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",  # "llama3:instruct",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(facts=facts),
            },
        ],
    )
    return MageResult(summary=response.choices[0].message.content)
