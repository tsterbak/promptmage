from nicegui import ui
from loguru import logger
from collections import defaultdict
from typing import List

from promptmage import PromptMage
from promptmage.prompt import Prompt
from .styles import label_with_icon


# Define a simple function to add custom styles for active tabs
def add_custom_css():
    ui.add_head_html(
        """
    <style>
        /* Subtle style for active tab */
        .q-tab--active {
            background-color: #e0f2ff !important; /* Light, soft blue background */
            color: #333 !important; /* Darker text for contrast */
            box-shadow: none !important; /* Remove any box shadow */
            transition: background-color 0.3s ease; /* Smooth transition for hover effects */
        }

        /* Change text color of q-chip in the active tab to primary */
        .q-tab--active .q-chip {
            color: var(--q-primary) !important; /* Applies the text-primary color */
        }

        /* Ensure q-chip text in inactive tabs remains secondary */
        .q-tab:not(.q-tab--active) .q-chip {
            color: var(--q-secondary) !important; /* Applies the text-secondary color */
        }

        /* Optional: Hover effect for the tab */
        .q-tab:hover {
            background-color: #f0f4f8 !important; /* Soft hover effect */
            color: #333 !important; /* Darker text for contrast */
        }
    </style>
    """
    )


def create_prompts_view(mage: PromptMage):
    # prompt editing dialog
    dialog = ui.dialog().props("full-width")
    # Add the custom styles to the head of the document
    add_custom_css()

    def create_prompt_content(prompts: List[Prompt]):
        content = ui.column().classes("w-full h-[88vh] p-10")
        with content:
            for prompt in sorted(prompts, key=lambda p: p.version, reverse=True):
                bg_color = ""
                # highlight active prompt in green
                if prompt.active:
                    bg_color = "bg-green-200 dark:bg-green-800"
                with ui.card().classes(bg_color).classes("p-5 w-full"):
                    # display run data
                    with ui.grid(columns=2).classes("gap-0"):
                        label_with_icon("Prompt ID:", icon="o_info")
                        ui.label(f"{prompt.id}")

                        label_with_icon("Name:", icon="o_badge")
                        ui.label(f"{prompt.name}")

                        label_with_icon("Version:", icon="o_tag")
                        ui.label(f"{prompt.version}")

                        label_with_icon("Active:", icon="o_check")
                        ui.label(f"{prompt.active}")

                        label_with_icon("System prompt:", icon="o_code")
                        ui.label(f"{prompt.system}")

                        label_with_icon("User prompt:", icon="o_psychology")
                        ui.label(f"{prompt.user}")

                    with ui.row():
                        activate_button = ui.button(
                            "Activate Prompt",
                            icon="o_play_circle_filled",
                            on_click=lambda prompt_id=prompt.id: activate_prompt(
                                prompt_id
                            ),
                        )
                        ui.button(
                            "Edit Prompt",
                            icon="o_edit",
                            on_click=lambda prompt_id=prompt.id: edit_prompt(prompt_id),
                        )
                        delete_button = ui.button(
                            "Delete Prompt",
                            icon="o_delete",
                            on_click=lambda prompt_id=prompt.id: delete_prompt(
                                prompt_id
                            ),
                        )
                        if prompt.active:
                            activate_button.disable()
                            delete_button.disable()
                        if not prompt.active:
                            delete_button.props("outline")
        return content

    def delete_prompt(prompt_id):
        logger.info(f"Deleting prompt with ID: {prompt_id}.")
        mage.prompt_store.delete_prompt(prompt_id)
        ui.notify(f"Prompt {prompt_id} deleted.")

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

    def activate_prompt(prompt_id):
        logger.info(f"Activating prompt with ID: {prompt_id}.")
        # activate the selected prompt
        prompt = mage.prompt_store.get_prompt_by_id(prompt_id)
        prompt.active = True
        mage.prompt_store.update_prompt(prompt)
        # deactivate all other prompts with the same name
        for p in mage.prompt_store.get_prompts():
            if p.name == prompt.name and p.id != prompt_id:
                p.active = False
                mage.prompt_store.update_prompt(p)
        ui.notify(f"Prompt {prompt_id} activated.")

    def save_prompt(prompt_id: str, system: str, user: str):
        prompt = mage.prompt_store.get_prompt_by_id(prompt_id)

        if (prompt.system != system) or (prompt.user != user):
            ui.notify("Prompt saved.")
        else:
            ui.notify("Prompt unchanged. Not saved.")

        prompt.system = system
        prompt.user = user
        mage.prompt_store.update_prompt(prompt)
        dialog.close()

    def build_ui():
        all_prompts = mage.prompt_store.get_prompts()
        # group them by name
        prompts = defaultdict(list)
        for prompt in all_prompts:
            if prompt.name in [step.prompt_name for step in mage.steps.values()]:
                prompts[prompt.name].append(prompt)

        # Main UI setup
        content = {name: prompts_for_name for name, prompts_for_name in prompts.items()}
        with ui.splitter(value=10).classes("w-full h-full") as splitter:
            with splitter.before:
                with ui.tabs().props("vertical").classes("w-full h-full") as tabs:
                    for title in content:
                        with ui.tab(title, label=title):
                            ui.chip(
                                f"{len(content[title])} versions", color="secondary"
                            ).props("outline square")
            with splitter.after:
                with ui.tab_panels(tabs, value=list(content.keys())[0]).props(
                    "vertical"
                ).classes("w-full h-full"):
                    for title, prompts_for_name in content.items():
                        with ui.tab_panel(title).classes("w-full h-full"):
                            create_prompt_content(prompts_for_name)

    return build_ui
