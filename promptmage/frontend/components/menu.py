from nicegui import ui


def menu() -> None:
    with ui.button_group():
        ui.button("Playground", on_click=lambda: ui.navigate.to("/")).classes(
            replace="text-white"
        )
        ui.button("Runs", on_click=lambda: ui.navigate.to("/runs")).classes(
            replace="text-white"
        )
        ui.button("Prompts", on_click=lambda: ui.navigate.to("/prompts")).classes(
            replace="text-white"
        )
