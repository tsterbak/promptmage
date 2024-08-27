from nicegui import ui
from typing import List
from slugify import slugify

from promptmage import PromptMage


def flow_card(flow: PromptMage):
    with ui.card().style("padding: 20px; margin: 10px;"):
        ui.button(
            f"{flow.name}", on_click=lambda: ui.navigate.to(f"/{slugify(flow.name)}")
        )
        ui.separator()
        ui.chip(f"{len(flow.steps)} Steps", icon="run_circle").props("square")
        runs = flow.get_run_data()
        ui.chip(f"{len(runs)} Runs", icon="check_circle").props("square")


def create_grid(elements, columns=4):
    rows = len(elements) // columns + (1 if len(elements) % columns > 0 else 0)
    for i in range(rows):
        with ui.row():
            for j in range(columns):
                index = i * columns + j
                if index < len(elements):
                    flow_card(elements[index])


def build_overview_page(flows: List[PromptMage]):
    with ui.column():
        ui.label("Available Flows").classes("font-bold text-lg")
        create_grid(flows, columns=4)
