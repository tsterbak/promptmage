from contextlib import contextmanager
from loguru import logger
from nicegui import ui, app


from .menu import menu


@contextmanager
def frame(navigation_title: str, flow_name: str = None, subtitle: str = None):
    """Custom page frame to share the same styling and behavior across all pages"""
    dark_mode_icon = None
    # load dark mode from local storage
    dark_value = app.storage.user.get("dark_mode", True)
    dark = ui.dark_mode(value=dark_value)

    def toggle_dark_mode():
        """Toggle dark mode on and off."""
        if dark.value:
            dark.disable()
            dark_mode_icon.name = "dark_mode"
        else:
            dark.enable()
            dark_mode_icon.name = "light_mode"
        # store dark mode in local storage
        app.storage.user["dark_mode"] = dark.value
        dark_mode_icon.update()

    # ui.colors(
    #    primary="#6E93D6", secondary="#53B689", accent="#111B1E", positive="#53B689"
    # )
    ui.colors(
        primary="#166088",
        secondary="#8fb9d2",
        accent="#FFFD98",
        dark="#13140b",
        positive="#21ba45",
        negative="#c10015",
        info="#bde4a7",
        warning="#f2c037",
    )

    with ui.header(elevated=True):
        with ui.button(on_click=lambda event: ui.navigate.to("/")).props(
            "flat color=white"
        ).classes("p-0"):
            ui.avatar("img:/static/promptmage-logo.png", square=True)

        if subtitle:
            with ui.column().classes("gap-0"):
                ui.label(navigation_title).classes("text-2xl")
                ui.label(subtitle).classes("text-sm text-gray-400")
        else:
            ui.label(navigation_title).classes("text-2xl self-center")
        ui.space()
        menu(flow_name=flow_name)
        with ui.button(
            on_click=toggle_dark_mode,
        ).props(
            "flat small color=white"
        ).classes("self-center"):
            dark_mode_icon = ui.icon("light_mode" if dark.value else "dark_mode")

    with ui.column().classes("self-center w-full gap-0"):
        yield
