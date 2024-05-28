"""This ui element represent the input, prompt and output of a callable step in the PromptMage."""

import inspect
from typing import Callable
from nicegui import ui

from promptmage import Prompt
from promptmage.storage import StorageBackend


def create_function_runner(
    func: Callable, prompt: Prompt, prompt_store: StorageBackend
):
    input_fields = {}
    system_prompt_field = None
    user_prompt_field = None
    result_field = None

    def run_function():
        inputs = {name: field.value for name, field in input_fields.items()}
        prompt.system = system_prompt_field.value
        prompt.user = user_prompt_field.value
        prompt_store.store_prompt(prompt)
        result = func(**inputs, prompt=prompt)
        result_field.set_content(f"{str(result)}")

    def build_ui():
        nonlocal user_prompt_field, system_prompt_field, result_field
        with ui.column().style(
            "border: 1px solid #ddd; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 20px; width: 600px; height: 800px; overflow-y: auto;"
        ):
            ui.label("Step Runner").style("font-weight: bold; font-size: 1.5em;")
            with ui.row():
                ui.label("Prompts:").style("width: 100px;")
                system_prompt_field = ui.textarea(value=prompt.system).style(
                    "flex-grow: 1; overflow: auto;"
                )
                user_prompt_field = ui.textarea(value=prompt.user).style(
                    "flex-grow: 1; overflow: auto;"
                )

            ui.label("Inputs:").style("margin-top: 20px; font-weight: bold;")
            for param in inspect.signature(func).parameters.values():
                if param.name != "prompt":
                    with ui.row():
                        ui.label(f"{param.name}:").style("width: 100px;")
                        input_fields[param.name] = ui.textarea().style(
                            "flex-grow: 1; overflow: auto;"
                        )

            ui.button("Run", on_click=run_function).style("margin-top: 10px;")
            ui.separator()
            ui.label("Result:").style("margin-top: 20px; font-weight: bold;")
            result_field = ui.markdown("").style(
                "margin-top: 20px; color: blue; height: 200px; overflow-y: auto;"
            )

    return build_ui
