"""This ui element represent the input, prompt and output of a callable step in the PromptMage."""

from nicegui import ui, run, app
from loguru import logger

from promptmage.mage import MageStep
from .styles import textbox_style


RUNNING_ICON = "run_circle"
NOT_RUNNING_ICON = "circle"
SUCCESS_RUN_ICON = "check_circle"


def create_function_runner(step: MageStep):
    input_fields = {}
    system_prompt_field = None
    user_prompt_field = None
    model_select = None
    result_field = None
    expansion_tab = ui.expansion(
        f"Step: {step.name}", group="steps", icon=f"{NOT_RUNNING_ICON}"
    ).classes("w-full text-lg")
    # load prompt if available
    if step.prompt_name:
        prompt = step.get_prompt()
    else:
        prompt = None

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
        expansion_tab.props("icon=run_circle")
        expansion_tab.update()
        inputs = {name: field.value for name, field in input_fields.items()}
        if prompt is not None:
            prompt.system = system_prompt_field.value
            prompt.user = user_prompt_field.value
        if model_select:
            logger.info(f"Selected model: {model_select.value}")
            step.model = model_select.value
        result = await run.io_bound(step.execute, **inputs)
        expansion_tab.props(f"icon={SUCCESS_RUN_ICON}")
        expansion_tab.update()

    def set_prompt():
        nonlocal prompt
        system_prompt_field.update()
        user_prompt_field.update()
        prompt.system = system_prompt_field.value
        prompt.user = user_prompt_field.value
        step.set_prompt(prompt)

    def update_inputs():
        for name, field in input_fields.items():
            field.set_value(step.input_values[name])
            field.update()
        expansion_tab.props(f"icon={RUNNING_ICON}")
        expansion_tab.update()

    def update_results():
        result_field.set_content(f"{step.result}")
        result_field.update()

        expansion_tab.props(f"icon={SUCCESS_RUN_ICON}")
        expansion_tab.update()

    step.on_input_change(update_inputs)
    step.on_output_change(update_results)

    def build_ui():
        nonlocal user_prompt_field, system_prompt_field, result_field, expansion_tab, model_select
        with expansion_tab.classes("w-full border"):
            ui.label(f"ID: {step.step_id}")
            with ui.column():
                # show available models if available
                if step.available_models:
                    with ui.row():
                        ui.label("Select model:").style("margin-top: 20px;")
                        model_select = ui.select(
                            step.available_models,
                            label="Select model",
                            value=step.model,
                        )
                with ui.row():
                    ui.label("Inputs:").style("margin-top: 20px; font-weight: bold;")
                    with ui.column().style("margin-top: 20px;").classes("w-full"):
                        for param in step.signature.parameters.values():
                            if param.name not in ["prompt", "model"]:
                                with ui.row():
                                    ui.label(f"{param.name}:")
                                    input_fields[param.name] = ui.textarea(
                                        value=step.input_values[param.name]
                                    ).classes(textbox_style)
                    ui.label("Prompts:").style("margin-top: 20px; font-weight: bold;")
                    with ui.column().style("margin-top: 20px;").classes("w-full"):
                        with ui.row().classes("w-full"):
                            ui.label("System:")
                            system_prompt_field = ui.textarea(
                                value=(
                                    prompt.system if prompt else "No prompt supported"
                                )
                            ).classes(textbox_style)
                        with ui.row().classes("w-full"):
                            ui.label("User:")
                            user_prompt_field = ui.textarea(
                                value=(prompt.user if prompt else "No prompt supported")
                            ).classes(textbox_style)

                with ui.row().classes("w-full"):
                    ui.button("Run", on_click=run_function).style("margin-top: 10px;")
                    ui.button("Save prompt", on_click=set_prompt).style(
                        "margin-top: 10px; margin-left: 10px;"
                    )
                ui.separator()
                with ui.row().classes("w-full"):
                    ui.label("Result:").style("margin-top: 20px; font-weight: bold;")
                    ui.button(
                        icon="content_copy",
                        on_click=lambda: ui.clipboard.write(
                            step.result or "No result available"
                        ),
                    ).props("fab")
                result_field = (
                    ui.markdown(f"{step.result}" if step.result else "")
                    .style("margin-top: 20px; color: blue;")
                    .classes("w-full")
                )

    return build_ui
