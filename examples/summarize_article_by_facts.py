from dotenv import load_dotenv
from openai import OpenAI

from promptmage import PromptMage, Prompt
from promptmage.storage import (
    SQLitePromptBackend,
    SQLiteDataBackend,
    PromptStore,
    DataStore,
)


load_dotenv()


client = OpenAI(
    # base_url="http://192.168.0.51:11434/v1",
    # api_key="ollama",  # required, but unused
)

# Create a new PromptMage instance
mage = PromptMage(
    name="fact-extraction",
    available_models=["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
)


# Application code


@mage.step(name="extract", prompt_name="extract_facts", depends_on=None)
def extract_facts(article: str, prompt: Prompt, model: str = "gpt-3.5-turbo") -> str:
    """Extract the facts as a bullet list from an article."""
    response = client.chat.completions.create(
        model=model,  # "llama3:instruct",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(article=article),
            },
        ],
    )
    return response.choices[0].message.content


@mage.step(name="summarize", prompt_name="summarize_facts", depends_on="extract")
def summarize_facts(facts: str, prompt: Prompt) -> str:
    """Summarize the given facts as a single sentence."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # "llama3:instruct",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(facts=facts),
            },
        ],
    )
    return response.choices[0].message.content
