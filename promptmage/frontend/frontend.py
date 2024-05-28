"""Frontend module for PromptMage."""

from fastapi import FastAPI
from nicegui import ui

from promptmage import PromptMage
from promptmage.mage import MageStep

from .components import theme
from .components.step_runner import create_function_runner
from .components.main_runner import create_main_runner


class PromptMageFrontend:
    """A class that creates a frontend for a PromptMage instance."""

    def __init__(self, mage: PromptMage):
        self.mage = mage

    def init_from_api(
        self, fastapi_app: FastAPI, favicon="../static/favicon.ico"
    ) -> None:
        """Initialize the frontend from a FastAPI application."""

        @ui.page("/", title="PromptMage")
        def main_page():
            with theme.frame("Welcome to the PromptMage"):
                with ui.row().style("flex-wrap: wrap;"):
                    with ui.column().style("flex-wrap: wrap;"):
                        with ui.card():
                            ui.label("Run all steps")
                            create_main_runner(self.mage)()
                            ui.update()

                    with ui.column().style("flex-wrap: wrap;"):
                        step: MageStep
                        for step in self.mage.steps.values():
                            with ui.expansion(
                                f"Step: {step.name}", icon="run_circle", group="steps"
                            ).classes("w-full").style("width: 650px;"):
                                with ui.card():
                                    ui.label(f"{step.name} - {step.step_id}")
                                    create_function_runner(step)()
                                    ui.update()

        ui.run_with(
            fastapi_app,
            mount_path="/gui",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
            storage_secret="pick your private secret here",  # NOTE setting a secret is optional but allows for persistent storage per user
        )
