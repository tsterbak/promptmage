"""This ui element represent the input, prompt and output of a callable step in the PromptMage."""

import inspect
from contextlib import contextmanager
from nicegui import ui, run

from promptmage import PromptMage
from .styles import textbox_style


@contextmanager
def create_main_runner(mage: PromptMage, execution_graph):
    input_fields = {}
    result_field = None
    flow_func = mage.get_run_function(start_from=None)

    async def run_function():
        inputs = {name: field.value for name, field in input_fields.items()}
        mage.is_running = True
        execution_graph.refresh()
        result = await run.io_bound(flow_func, **inputs)
        newline = "\n\n"
        if isinstance(result, list):
            result_field.set_content(
                f"{[newline.join(res.values()) for res in result]}"
            )
        else:
            result_field.set_content(f"{newline.join(result.values())}")
        result_field.update()
        execution_graph.refresh()

    def build_ui():
        nonlocal result_field
        with ui.column().classes("w-full"):
            # elements before the steps runner
            ui.label("Inputs:").classes("font-bold text-lg")
            for param in inspect.signature(flow_func).parameters.values():
                if param.name not in ["prompt", "model"]:
                    with ui.row().classes("w-full"):
                        input_fields[param.name] = (
                            ui.textarea(label=f"{param.name}")
                            .classes(textbox_style)
                            .props("outlined")
                        )

            with ui.row().classes("w-full justify-end"):
                ui.button("Run", on_click=run_function)
            ui.separator()
            # steps runner
            ui.label("Steps:").classes("font-bold text-lg")
            yield
            # elements after the steps runner
            ui.separator()
            with ui.row().classes("w-full justify-between"):
                ui.label("Result:").classes("font-bold text-lg")
                ui.button(
                    "Copy to clipboard",
                    on_click=lambda: ui.clipboard.write(result_field.content),
                )  # .props("fab")
            result_field = (
                ui.markdown("")
                .style("height: 200px; overflow-y: auto;")
                .classes("color-black dark:color-white")
            )

    return build_ui()
