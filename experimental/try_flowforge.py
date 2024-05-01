from time import sleep

from experimental.src.functions import multiply

import flowforgeai as ff


flow = ff.FlowForge("flow")


@flow.step("step_one", prompt_id="prompt_one")
def step_one(a: int, b: int, prompt: ff.Prompt) -> int:
    print("Step one")
    print(prompt)
    return multiply(a, b)


@flow.step("step_two")
def step_two(a: int, b: str) -> str:
    print("Step two")
    sleep(1)
    return f"Step two result {a}"


@flow.step("step_three")
def step_three() -> str:
    print("Step three")
    sleep(1)
    return "Step three result"
