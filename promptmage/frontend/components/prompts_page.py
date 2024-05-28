from promptmage.storage.prompt_store import PromptStore

from nicegui import ui


def create_prompts_view(prompt_store: PromptStore):

    def build_ui():
        with ui.column():
            ui.label("Prompts")
            prompts = prompt_store.get_prompts()
            prompts_dict = {prompt.id: prompt.to_dict() for prompt in prompts}
            for prompt_id, prompt in prompts_dict.items():
                with ui.card():
                    with ui.expansion(
                        f"Prompt {prompt_id} with name \"{prompt['name']}\""
                    ).classes("w-full"):
                        ui.label(f"Name: {prompt['name']}")
                        ui.label(f"ID: {prompt['id']}")
                        ui.label(f"System: {prompt['system']}")
                        ui.label(f"User: {prompt['user']}")
                        ui.label(f"Version: {prompt['version']}")
                        ui.label(f"Template Variables: {prompt['template_vars']}")
                        with ui.row():
                            ui.button(
                                "Use Prompt",
                                on_click=lambda prompt_id=prompt_id: prompt_store.use_prompt(
                                    prompt_id
                                ),
                            )
                            ui.button(
                                "Edit Prompt",
                                on_click=lambda prompt_id=prompt_id: prompt_store.edit_prompt(
                                    prompt_id
                                ),
                            )
                            ui.button(
                                "Delete Prompt",
                                on_click=lambda prompt_id=prompt_id: prompt_store.delete_prompt(
                                    prompt_id
                                ),
                            )
                    ui.update()

    return build_ui
