"""Frontend module for PromptMage."""

from fastapi import FastAPI
from nicegui import ui

from promptmage import PromptMage
from promptmage.mage import MageStep

from .components import theme
from .components.main_runner import create_main_runner
from .components.step_runner import create_function_runner
from .components.runs_page import create_runs_view
from .components.prompts_page import create_prompts_view


class PromptMageFrontend:
    """A class that creates a frontend for a PromptMage instance."""

    def __init__(self, mage: PromptMage):
        self.mage = mage

    def init_from_api(self, fastapi_app: FastAPI) -> None:
        """Initialize the frontend from a FastAPI application."""

        @ui.page("/", title="PromptMage")
        def main_page():
            with theme.frame("Welcome to the PromptMage"):
                with ui.row().style("flex-wrap: wrap;"):
                    # Create a card for the mage
                    with ui.column().style("flex-wrap: wrap;"):
                        with ui.card():
                            ui.label("Run all steps")
                            create_main_runner(self.mage)()
                    # Create a card for each step
                    with ui.column().style("flex-wrap: wrap;"):
                        step: MageStep
                        for step in self.mage.steps.values():
                            create_function_runner(step)()

        @ui.page("/runs", title="PromptMage - Runs")
        def runs_page():
            with theme.frame("Runs"):
                create_runs_view(self.mage.data_store)()

        @ui.page("/prompts", title="PromptMage - Prompts")
        def prompts_page():
            with theme.frame("Prompts"):
                create_prompts_view(self.mage.prompt_store)()

        ui.run_with(
            fastapi_app,
            mount_path="/gui",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
            storage_secret="pick your private secret here",  # NOTE setting a secret is optional but allows for persistent storage per user
            dark=False,
            favicon="🧙",
        )
