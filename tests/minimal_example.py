from promptmage import PromptMage, Prompt, MageResult
from promptmage.storage import (
    PromptStore,
    DataStore,
    SQLiteDataBackend,
    SQLitePromptBackend,
)

prompt_store = PromptStore(backend=SQLitePromptBackend(":memory:"))
prompt_store.store_prompt(
    Prompt(
        name="prompt1",
        system="system1",
        user="user1",
        template_vars=["question"],
        version=1,
        active=True,
    )
)

mage = PromptMage(
    name="example",
    prompt_store=prompt_store,
    data_store=DataStore(backend=SQLiteDataBackend(":memory:")),
)


@mage.step(name="step1", prompt_name="prompt1", initial=True)
def step1(question: str, prompt: Prompt) -> MageResult:
    answer = f"Answer to {question}"
    return MageResult(next_step=None, result=answer)
