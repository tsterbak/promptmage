"""Frontend module for PromptMage."""

from fastapi import FastAPI
from nicegui import ui

from promptmage import PromptMage

from .components import theme
from .components.step_runner import create_function_runner


class PromptMageFrontend:

    def __init__(self, mage: PromptMage):
        self.mage = mage

    def init_from_api(self, fastapi_app: FastAPI) -> None:
        @ui.page("/", title="PromptMage")
        def main_page():
            with theme.frame("Welcome to the PromptMage"):
                with ui.row().style("flex-wrap: wrap;"):
                    for step_func in self.mage.steps.values():
                        with ui.card():
                            ui.label(step_func.__name__)
                            create_function_runner(
                                step_func,
                                self.mage.backend.get_prompt(step_func.__name__),
                            )()

        ui.run_with(
            fastapi_app,
            mount_path="/gui",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
            storage_secret="pick your private secret here",  # NOTE setting a secret is optional but allows for persistent storage per user
            favicon="static/favicon.ico",  # NOTE this is optional and can be omitted
        )
