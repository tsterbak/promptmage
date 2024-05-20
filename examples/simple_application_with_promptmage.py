from openai import OpenAI

from promptmage import PromptMage, Prompt
from promptmage.storage import InMemoryBackend


client = OpenAI(
    base_url="http://192.168.0.51:11434/v1",
    api_key="ollama",  # required, but unused
)

backend = InMemoryBackend(
    prompts={
        "extract_facts": Prompt(
            prompt_id="extract_facts",
            system_prompt="You are a helpful assistant.",
            user_prompt="Extract the facts from this article and return the results as a markdown list:\n\n<article>{article}</article> Make sure to include all the important details and don't make up any information.",
        ),
        "summarize_facts": Prompt(
            prompt_id="summarize_facts",
            system_prompt="You are a helpful assistant.",
            user_prompt="Summarize the following facts into a single sentence:\n\n{facts}",
        ),
    }
)
mage = PromptMage(name="fact-extraction", backend=backend)


@mage.step(name="extract", prompt_id="extract_facts")
def extract_facts(article: str, prompt: Prompt) -> str:
    """Extract the facts as a bullet list from an article."""

    response = client.chat.completions.create(
        model="llama3:instruct",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(article=article),
            },
        ],
    )
    return response.choices[0].message.content


@mage.step(name="summarize", prompt_id="summarize_facts")
def summarize_facts(facts: str, prompt: Prompt) -> str:
    """Summarize the given facts as a single sentence."""
    response = client.chat.completions.create(
        model="llama3:instruct",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(facts=facts),
            },
        ],
    )
    return response.choices[0].message.content
