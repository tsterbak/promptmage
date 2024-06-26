from contextlib import contextmanager
from nicegui import ui

from .menu import menu


@contextmanager
def frame(navigation_title: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(
        primary="#6E93D6", secondary="#53B689", accent="#111B1E", positive="#53B689"
    )
    with ui.header(elevated=True):
        with ui.link("/"):
            ui.avatar("img:/static/promptmage-logo.png")
        # ui.image("/static/promptmage-logo.png").classes("w-16")
        ui.space()
        ui.label(navigation_title).style("font-size: 1.5em;")
        ui.space()
        menu()
    with ui.column():  # .classes("absolute-center items-center"):
        yield
