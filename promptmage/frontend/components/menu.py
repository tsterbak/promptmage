from nicegui import ui


def menu(flow_name: str) -> None:
    with ui.button_group().classes("self-center"):
        ui.button("Overview", on_click=lambda: ui.navigate.to("/")).classes(
            replace="text-white"
        )
        ui.button(
            "Playground", on_click=lambda: ui.navigate.to(f"/{flow_name}")
        ).classes(replace="text-white")
        ui.button(
            "Runs", on_click=lambda: ui.navigate.to(f"/runs/{flow_name}")
        ).classes(replace="text-white")
        ui.button(
            "Prompts", on_click=lambda: ui.navigate.to(f"/prompts/{flow_name}")
        ).classes(replace="text-white")
        ui.button(
            "Evaluation", on_click=lambda: ui.navigate.to(f"/evaluation/{flow_name}")
        ).classes(replace="text-white")
