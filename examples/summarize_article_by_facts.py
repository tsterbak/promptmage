import json
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

from promptmage import PromptMage, Prompt, MageResult

load_dotenv()


client = OpenAI()

# Create a new PromptMage instance
mage = PromptMage(
    name="fact-extraction",
    available_models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
)


# Application code #


@mage.step(name="extract", prompt_name="extract_facts", initial=True)
def extract_facts(
    article: str, prompt: Prompt, model: str = "gpt-3.5-turbo"
) -> List[str]:
    """Extract the facts as a bullet list from an article."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(article=article),
            },
        ],
    )
    raw_facts = response.choices[0].message.content
    raw_facts = raw_facts.replace("```json", "").strip("```").strip()
    return MageResult(
        next_step="check_facts", fact=[str(f) for f in json.loads(raw_facts)]
    )


@mage.step(
    name="check_facts",
    prompt_name="check_facts",
    one_to_many=True,
)
def check_facts(fact: str, prompt: Prompt) -> str:
    """Check the extracted facts for accuracy."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(fact=fact),
            },
        ],
    )
    return MageResult(
        next_step="summarize",
        check_results=f"Fact: {fact}\n\nCheck result: {response.choices[0].message.content}",
    )


@mage.step(
    name="summarize",
    prompt_name="summarize_facts",
    many_to_one=True,
)
def summarize_facts(check_results: str, prompt: Prompt) -> str:
    """Summarize the given facts as a single sentence."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt.system},
            {
                "role": "user",
                "content": prompt.user.format(check_result=check_results),
            },
        ],
    )
    return MageResult(result=response.choices[0].message.content)
