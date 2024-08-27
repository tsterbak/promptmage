"""This ui element represent the input, prompt and output of a callable step in the PromptMage."""

from nicegui import ui, run, app
from typing import List
from loguru import logger

from promptmage.mage import MageStep
from .styles import textbox_style


RUNNING_ICON = "run_circle"
NOT_RUNNING_ICON = "circle"
SUCCESS_RUN_ICON = "check_circle"


class InputOutputSection:

    def __init__(self, step: MageStep):
        self.step = step

        self.fields = {}

    @ui.refreshable
    def ui(self):
        ui.label("Inputs:").classes("font-bold mr-5")
        for param in self.step.signature.parameters.values():
            if param.name not in ["prompt", "model"]:
                with ui.row():
                    self.fields[param.name] = (
                        ui.textarea(
                            label=f"{param.name}",
                            value=self.step.input_values[param.name],
                        )
                        .classes(textbox_style)
                        .props("outlined")
                    )


def create_function_runner(step: MageStep):
    input_output_section = InputOutputSection(step)
    system_prompt_field = None
    user_prompt_field = None
    model_select = None
    result_field = None
    expansion_tab = ui.expansion(
        f"Step: {step.name}", group="steps", icon=f"{NOT_RUNNING_ICON}"
    ).classes("text-lg w-full border")
    # load prompt if available
    if step.prompt_name:
        prompt = step.get_prompt()
        # load all available prompts for the step
        prompts = [
            p for p in step.prompt_store.get_prompts() if p.name == step.prompt_name
        ]
    else:
        prompt = None
        prompts = []

    # run id given in app.storage, initialize with this data
    if app.storage.user.get("step_run_id"):
        step_run_id = app.storage.user.get("step_run_id")
        run_data = step.data_store.get_data(step_run_id)
        if run_data.step_name == step.name:
            prompt = run_data.prompt
            step.input_values = run_data.input_data
            step.result = run_data.output_data
            expansion_tab.props(f"icon={SUCCESS_RUN_ICON}")
            expansion_tab.update()
            del app.storage.user["step_run_id"]

    async def run_function():
        expansion_tab.props(f"icon={RUNNING_ICON}")
        expansion_tab.update()
        inputs = {
            name: field.value for name, field in input_output_section.fields.items()
        }
        if prompt is not None:
            prompt.system = system_prompt_field.value
            prompt.user = user_prompt_field.value
        if model_select:
            logger.info(f"Selected model: {model_select.value}")
            step.model = model_select.value
        _ = await run.io_bound(step.execute, **inputs, prompt=prompt)
        if step.one_to_many:
            num_results = len(step.result.results)
            expansion_tab.props(f"caption='{num_results} results'")
        expansion_tab.props(f"icon={SUCCESS_RUN_ICON}")
        expansion_tab.update()

    def set_prompt():
        nonlocal prompt
        system_prompt_field.update()
        user_prompt_field.update()
        if (prompt.system != system_prompt_field.value) or (
            prompt.user != user_prompt_field.value
        ):
            prompt.system = system_prompt_field.value
            prompt.user = user_prompt_field.value
            step.set_prompt(prompt)
            ui.notify("Prompt saved.")
        else:
            ui.notify("Prompt unchanged. Not saved.")

    def update_inputs():
        for name, field in input_output_section.fields.items():
            field.set_value(step.input_values[name])
            field.update()
        expansion_tab.props(f"icon={RUNNING_ICON}")
        expansion_tab.update()

    def update_results():
        newline = "\n\n"
        if isinstance(step.result, list):
            result_field.set_content(
                f"{[newline.join(result.results.values()) for result in step.result]}"
            )
        else:
            result_field.set_content(f"{newline.join(step.result.results.values())}")
        result_field.update()

        expansion_tab.props(f"icon={SUCCESS_RUN_ICON}")
        if isinstance(step.result, list):
            num_results = len(step.result)
            expansion_tab.props(f"caption='{num_results} results'")
        expansion_tab.update()

    def display_prompt(prompt_str: str):
        nonlocal prompt
        logger.info(f"Selected prompt: {prompt_str}")
        prompt_name, version = prompt_str.split(" - v")
        prompt = step.prompt_store.get_prompt(prompt_name, version=int(version))
        system_prompt_field.set_value(prompt.system)
        user_prompt_field.set_value(prompt.user)
        system_prompt_field.update()
        user_prompt_field.update()

    step.on_input_change(update_inputs)
    step.on_output_change(update_results)

    def build_ui():
        nonlocal user_prompt_field, system_prompt_field, result_field, expansion_tab, model_select
        with expansion_tab:
            ui.label(f"ID: {step.step_id}")
            with ui.column().classes("w-full"):
                with ui.row().classes("w-full"):
                    # show available models if available
                    if step.available_models:
                        model_select = ui.select(
                            step.available_models,
                            label="Select model",
                            value=step.model,
                        ).classes("w-1/3")
                    # show available prompts
                    prompt_select = ui.select(
                        [f"{p.name} - v{p.version}" for p in prompts],
                        label="Select prompt",
                        value=(
                            f"{prompt.name} - v{prompt.version}"
                            if prompt
                            else "No prompt selected"
                        ),
                        on_change=lambda event: display_prompt(event.value),
                    ).classes("w-1/3")

                with ui.row().classes("w-full"):
                    ui.label("Prompts:").classes("font-bold")
                    with ui.row().classes("grow"):
                        system_prompt_field = (
                            ui.textarea(
                                label="System prompt:",
                                value=(
                                    prompt.system if prompt else "No prompt supported"
                                ),
                            )
                            .classes(textbox_style)
                            .props("outlined")
                        )
                    with ui.row().classes("grow"):
                        user_prompt_field = (
                            ui.textarea(
                                label="User prompt:",
                                value=(
                                    prompt.user if prompt else "No prompt supported"
                                ),
                            )
                            .classes(textbox_style)
                            .props("outlined")
                        )
                with ui.row():
                    input_output_section.ui()

                with ui.row().classes("w-full justify-end"):
                    ui.button("Run", on_click=run_function)
                    ui.button("Save prompt", on_click=set_prompt)
                ui.separator()
                with ui.row().classes("w-full justify-between"):
                    ui.label("Result:").classes("font-bold")
                    ui.button(
                        "Copy to clipboard",
                        on_click=lambda: ui.clipboard.write(
                            step.result or "No result available"
                        ),
                    )
                result_field = (
                    ui.markdown(f"{step.result}" if step.result else "")
                    .style("margin-top: 20px;")
                    .classes("color-black dark:color-white")
                )

    return build_ui
