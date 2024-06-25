from nicegui import ui
from loguru import logger
from collections import defaultdict
from typing import List

from promptmage import PromptMage
from promptmage.prompt import Prompt


def create_prompts_view(mage: PromptMage):
    side_panel = ui.element("div").style(
        "position: fixed; top: 0; right: 0; width: 50%; height: 100%; background-color: #f0f0f0; transform: translateX(100%); transition: transform 0.3s ease; z-index: 1000; overflow-y: auto;"
    )

    # prompt editing dialog
    dialog = ui.dialog().props("full-width")

    # Function to show the side panel with detailed information
    def show_side_panel(prompts: List[Prompt]):
        # get prompt with highest version
        side_panel.clear()
        with side_panel:
            ui.button(">>", on_click=hide_side_panel).style(
                "margin: 20px; margin-bottom: 0px; margin-top: 100px;"
            )
            for prompt in sorted(prompts, key=lambda p: p.version, reverse=True):
                with ui.card().style(
                    "padding: 20px; margin-right: 20px; margin-top: 10px; margin-bottom: 10px; margin-left: 20px"
                ):
                    # display run data
                    ui.label(f"Prompt ID: {prompt.id}")
                    ui.label(f"Name: {prompt.name}")
                    ui.label(f"Version: {prompt.version}")
                    ui.label(f"System prompt: {prompt.system}")
                    ui.label(f"User prompt: {prompt.user}")
                    with ui.row():
                        ui.button(
                            "Use Prompt",
                            on_click=lambda prompt_id=prompt.id: use_prompt(prompt_id),
                        )
                        ui.button(
                            "Edit Prompt",
                            on_click=lambda prompt_id=prompt.id: edit_prompt(prompt_id),
                        )
                        ui.button(
                            "Delete Prompt",
                            on_click=lambda prompt_id=prompt.id: delete_prompt(
                                prompt_id
                            ),
                        )
        side_panel.style("transform:translateX(0%);")
        side_panel.update()

    def delete_prompt(prompt_id):
        logger.info(f"Deleting prompt with ID: {prompt_id}.")
        mage.prompt_store.delete_prompt(prompt_id)

    def edit_prompt(prompt_id):
        logger.info(f"Editing prompt with ID: {prompt_id}.")
        prompt = mage.prompt_store.get_prompt_by_id(prompt_id)
        dialog.clear()
        with dialog, ui.card():
            ui.label("Edit prompt").classes("text-2xl")
            with ui.row():
                ui.label(f"Name: {prompt.name}")
                ui.label(f"Version: {prompt.version}")
                ui.label(f"Prompt ID: {prompt_id}")
            with ui.row():
                system_prompt = ui.textarea(
                    value=prompt.system, label="System prompt"
                ).style("width: 500px; height: 200px;")
                user_prompt = ui.textarea(value=prompt.user, label="User prompt").style(
                    "width: 500px; height: 200px;"
                )
            with ui.row():
                ui.button(
                    "Save",
                    on_click=lambda: save_prompt(
                        prompt_id, system_prompt.value, user_prompt.value
                    ),
                )
                ui.button("Cancel", on_click=dialog.close)

        dialog.open()

    def use_prompt(prompt_id):
        logger.info(f"Using prompt with ID: {prompt_id}. Not implemented yet.")

    def save_prompt(prompt_id: str, system: str, user: str):
        prompt = mage.prompt_store.get_prompt_by_id(prompt_id)
        prompt.system = system
        prompt.user = user
        mage.prompt_store.update_prompt(prompt)
        dialog.close()

    # Function to hide the side panel
    def hide_side_panel():
        side_panel.clear()
        side_panel.style("transform:translateX(100%);")
        side_panel.update()

    def build_ui():
        ui.label("Prompts").classes("text-2xl")
        all_prompts = mage.prompt_store.get_prompts()
        # group them by name
        prompts = defaultdict(list)
        for prompt in all_prompts:
            if prompt.name in [step.prompt_name for step in mage.steps.values()]:
                prompts[prompt.name].append(prompt)

        # Main UI setup
        with ui.card().style("padding: 20px"):
            # Create a table with clickable rows
            columns = [
                {"name": "name", "label": "name", "field": "name", "sortable": True},
                {
                    "name": "versions",
                    "label": "Number of versions",
                    "field": "versions",
                    "sortable": True,
                },
            ]

            rows = [
                {
                    "name": name,
                    "versions": len(prompts_for_name),
                }
                for name, prompts_for_name in prompts.items()
            ]

            table = ui.table(columns=columns, rows=rows)

            def on_row_click(event):
                selected_run_index = event.args[-2]["name"]
                show_side_panel(prompts=prompts[selected_run_index])

            table.on("rowClick", on_row_click)

    return build_ui
