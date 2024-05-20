from openai import OpenAI

client = OpenAI(
    base_url="http://192.168.0.51:11434/v1",
    api_key="ollama",  # required, but unused
)


def extract_facts(article: str) -> str:
    """Extract the facts as a bullet list from an article."""

    response = client.chat.completions.create(
        model="llama3:instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Extract the facts from this article and return the results as a markdown list:\n\n<article>{article}</article> Make sure to include all the important details and don't make up any information.",
            },
        ],
    )
    return response.choices[0].message.content


def summarize_facts(facts: str) -> str:
    """Summarize the given facts as a single sentence."""
    response = client.chat.completions.create(
        model="llama3:instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Summarize the following facts into a single sentence:\n\n{facts}",
            },
        ],
    )
    return response.choices[0].message.content


def main(article: str):
    facts = extract_facts(article)
    print(facts)

    summary = summarize_facts(facts)
    print(summary)


if __name__ == "__main__":
    article = """
    The 2022 Winter Olympics, officially known as the XXIV Olympic Winter Games, is an international multi-sport event scheduled to take place from 4 to 20 February 2022 in Beijing and towns in the neighboring Hebei province, China. The Games will feature 109 events over 15 disciplines in 7 sports, making it the first Winter Olympics to surpass 100 medal events. The 2022 Winter Olympics will be the first Winter Olympics to be held in China, the second Olympics to be held in China after the 2008 Summer Olympics in Beijing, and the fourth Olympics overall to be held in China after the 2008 Summer Olympics, the 2014 Summer Youth Olympics in Nanjing, and the 2014 Winter Youth Olympics in Lillehammer.
    """

    main(article=article)
