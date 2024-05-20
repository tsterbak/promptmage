"""Frontend module for PromptMage."""

from fastapi import FastAPI
from nicegui import app, ui

from promptmage import PromptMage


class PromptMageFrontend:

    def __init__(self, mage: PromptMage):
        self.mage = mage

    def init_from_api(self, fastapi_app: FastAPI) -> None:
        @ui.page("/")
        def show():
            ui.label("Hello, FastAPI!")

            # NOTE dark mode will be persistent for each user across tabs and server restarts
            ui.dark_mode().bind_value(app.storage.user, "dark_mode")
            ui.checkbox("dark mode").bind_value(app.storage.user, "dark_mode")

        ui.run_with(
            fastapi_app,
            mount_path="/gui",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
            storage_secret="pick your private secret here",  # NOTE setting a secret is optional but allows for persistent storage per user
        )
