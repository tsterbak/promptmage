"""This ui element represent the input, prompt and output of a callable step in the PromptMage."""

import inspect
from nicegui import ui, run

from promptmage import PromptMage
from .styles import textbox_style


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
        with ui.column().classes("w-full"):
            ui.label("Inputs:").style("margin-top: 20px; font-weight: bold;")
            for param in inspect.signature(flow_func).parameters.values():
                if param.name not in ["prompt", "model"]:
                    with ui.row().classes("w-full"):
                        ui.label(f"{param.name}:").style("width: 100px;")
                        input_fields[param.name] = (
                            ui.textarea()
                            .classes(textbox_style)
                            .style("padding-top: 0px;")
                        )

            ui.button("Run", on_click=run_function).style("margin-top: 10px;")
            ui.separator()
            with ui.row().classes("w-full"):
                ui.button(
                    icon="content_copy",
                    on_click=lambda: ui.clipboard.write(result_field.content),
                ).props("fab")
                ui.label("Result:").style("margin-top: 20px; font-weight: bold;")
            result_field = ui.markdown("").style(
                "margin-top: 20px; color: blue; height: 200px; overflow-y: auto;"
            )

    return build_ui
