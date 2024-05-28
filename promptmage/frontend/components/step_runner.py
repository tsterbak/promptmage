"""This ui element represent the input, prompt and output of a callable step in the PromptMage."""

from nicegui import ui, run

from promptmage.mage import MageStep


RUNNING_ICON = "run_circle"
NOT_RUNNING_ICON = "circle"
SUCCESS_RUN_ICON = "check_circle"


def create_function_runner(step: MageStep):
    input_fields = {}
    system_prompt_field = None
    user_prompt_field = None
    result_field = None
    expansion_tab = (
        ui.expansion(f"Step: {step.name}", group="steps", icon=f"{NOT_RUNNING_ICON}")
        .classes("w-full")
        .style("width: 650px;")
    )
    prompt = step.get_prompt()

    async def run_function():
        expansion_tab.props("icon=run_circle")
        expansion_tab.update()
        inputs = {name: field.value for name, field in input_fields.items()}
        prompt.system = system_prompt_field.value
        prompt.user = user_prompt_field.value
        step.set_prompt(prompt)
        result = await run.io_bound(step.execute, **inputs)
        expansion_tab.props(f"icon={SUCCESS_RUN_ICON}")
        expansion_tab.update()

    def set_prompt():
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
        nonlocal user_prompt_field, system_prompt_field, result_field, expansion_tab
        with expansion_tab:
            with ui.card():
                ui.label(f"{step.name} - {step.step_id}")
                with ui.column().style(
                    "border: 1px solid #ddd; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 20px; width: 1000px; height: 700px; overflow-y: auto;"
                ):
                    ui.label("Step Runner").style(
                        "font-weight: bold; font-size: 1.5em;"
                    )
                    with ui.row():
                        ui.label("Inputs:").style(
                            "margin-top: 20px; font-weight: bold;"
                        )
                        with ui.column().style("flex-grow: 1; margin-top: 20px;"):
                            for param in step.signature.parameters.values():
                                if param.name != "prompt":
                                    with ui.row():
                                        ui.label(f"{param.name}:").style(
                                            "width: 100px;"
                                        )
                                        input_fields[param.name] = ui.textarea(
                                            value=step.input_values[param.name]
                                        ).style("flex-grow: 1; overflow: auto;")
                        ui.label("Prompts:").style(
                            "margin-top: 20px; font-weight: bold;"
                        )
                        with ui.column().style("flex-grow: 1; margin-top: 20px;"):
                            with ui.row():
                                ui.label("System:").style("width: 100px;")
                                system_prompt_field = ui.textarea(
                                    value=prompt.system
                                ).style("flex-grow: 1; overflow: auto;")
                            with ui.row():
                                ui.label("User:").style("width: 100px;")
                                user_prompt_field = ui.textarea(
                                    value=prompt.user
                                ).style("flex-grow: 1; overflow: auto;")

                    with ui.row():
                        ui.button("Run", on_click=run_function).style(
                            "margin-top: 10px;"
                        )
                        ui.button("Set prompt", on_click=set_prompt).style(
                            "margin-top: 10px; margin-left: 10px;"
                        )
                    ui.separator()
                    ui.label("Result:").style("margin-top: 20px; font-weight: bold;")
                    result_field = ui.markdown(
                        f"{step.result}" if step.result else ""
                    ).style(
                        "margin-top: 20px; color: blue; height: 200px; overflow-y: auto;"
                    )

    return build_ui
