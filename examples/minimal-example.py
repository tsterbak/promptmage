from promptmage import PromptMage, Prompt, MageResult

mage = PromptMage(
    name="example",
)


@mage.step(name="step1", prompt_name="prompt1", initial=True)
def step1(question: str, prompt: Prompt) -> MageResult:
    answer = f"Answer to {question}"
    return MageResult(next_step=None, result=answer)
