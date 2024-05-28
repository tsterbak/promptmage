"""This ui element represent the input, prompt and output of a callable step in the PromptMage."""

import inspect
from nicegui import ui, run
from loguru import logger

from promptmage import PromptMage


def create_main_runner(mage: PromptMage):
    input_fields = {}
    result_field = None
    flow_func = mage.get_run_function(start_from=None)

    async def run_function():
        inputs = {name: field.value for name, field in input_fields.items()}
        result = await run.io_bound(flow_func, **inputs)
        result_field.set_content(f"{str(result)}")
        result_field.update()

    def build_ui():
        nonlocal result_field
        with ui.column().style(
            "border: 1px solid #ddd; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 20px; width: 600px; height: 800px; overflow-y: auto;"
        ):
            ui.label("Flow Runner").style("font-weight: bold; font-size: 1.5em;")
            ui.label("Inputs:").style("margin-top: 20px; font-weight: bold;")
            for param in inspect.signature(flow_func).parameters.values():
                if param.name != "prompt":
                    with ui.row():
                        ui.label(f"{param.name}:").style("width: 100px;")
                        input_fields[param.name] = ui.textarea().style(
                            "flex-grow: 2; overflow: auto;"
                        )

            ui.button("Run", on_click=run_function).style("margin-top: 10px;")
            ui.separator()
            ui.label("Result:").style("margin-top: 20px; font-weight: bold;")
            result_field = ui.markdown("").style(
                "margin-top: 20px; color: blue; height: 200px; overflow-y: auto;"
            )

    return build_ui
