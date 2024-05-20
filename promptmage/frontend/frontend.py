"""Frontend module for PromptMage."""

from fastapi import FastAPI
from nicegui import app, ui

from promptmage import PromptMage

from .components import theme
from promptmage.frontend.components.message import message


class PromptMageFrontend:

    def __init__(self, mage: PromptMage):
        self.mage = mage

    def init_from_api(self, fastapi_app: FastAPI) -> None:
        @ui.page("/")
        def main_page():
            with theme.frame("- Page A -"):
                message("Page A")
                ui.label("This page is defined in a function.")

        ui.run_with(
            fastapi_app,
            mount_path="/gui",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
            storage_secret="pick your private secret here",  # NOTE setting a secret is optional but allows for persistent storage per user
        )
