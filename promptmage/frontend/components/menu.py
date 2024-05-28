from nicegui import ui


def menu() -> None:
    ui.link("Home", "/").classes(replace="text-white")
    ui.link("Runs", "/runs").classes(replace="text-white")
    ui.link("Prompts", "/prompts").classes(replace="text-white")
