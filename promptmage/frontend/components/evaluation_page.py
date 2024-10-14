from nicegui import ui
from typing import List
from slugify import slugify
from loguru import logger

from promptmage import PromptMage


def dataset_card(dataset, flow):
    datapoints = flow.data_store.backend.get_datapoints(dataset.id)
    is_done = all([dp.rating is not None for dp in datapoints])
    with ui.card().style("padding: 20px; margin: 10px;"):
        with ui.row().classes("items-center"):
            if is_done:
                ui.icon("check_circle").style("color: green; font-size: 24px;")
            else:
                ui.icon("o_pending").style("color: orange; font-size: 24px;")
            ui.label(f"{dataset.name}").classes("text-lg")
        ui.separator()
        with ui.row().classes("justify-between"):
            with ui.column():
                ui.label("Datapoints")
                ui.label("Progress")
                ui.label("Average rating")
            with ui.column():
                ui.label(f"{len(datapoints)}")
                ui.label(
                    f"{len([dp for dp in datapoints if dp.rating is not None]) / len(datapoints) * 100:.1f}%"
                )
                ui.label(
                    f"{sum([dp.rating for dp in datapoints if dp.rating is not None]) / len(datapoints):.2f}"
                )
        ui.separator()
        with ui.row().classes("justify-between"):
            ui.button(
                "Delete",
                icon="o_delete",
                on_click=lambda: delete_dataset(dataset.id, flow),
            ).style("color: red;").props("outline")
            ui.button(
                "Go to dataset",
                icon="o_arrow_forward",
                on_click=lambda: ui.navigate.to(
                    f"/evaluation/{slugify(flow.name)}/{dataset.id}"
                ),
            )


def create_dataset(name: str, flow: PromptMage):
    flow.data_store.backend.create_dataset(name)
    logger.info(f"Created dataset: {name}")


def delete_dataset(dataset_id: str, flow: PromptMage):
    flow.data_store.backend.delete_dataset(dataset_id)
    logger.info(f"Deleted dataset: {dataset_id}")


def create_grid(elements, flow, columns: int = 4):
    elements.insert(0, None)
    rows = len(elements) // columns + (1 if len(elements) % columns > 0 else 0)
    if rows == 0:
        rows = 1
    for i in range(rows):
        with ui.row().classes("justify-center"):
            for j in range(columns):
                if i == j == 0:
                    with ui.card().style("padding: 20px; margin: 10px;"):
                        dataset_name = ui.label("New dataset")
                        dataset_name.set_visibility(False)
                        ui.input(
                            label="New dataset name",
                            placeholder="Start typing",
                            on_change=lambda e: dataset_name.set_text(e.value),
                        )
                        ui.button(
                            "Create dataset",
                            icon="add",
                            on_click=lambda: create_dataset(dataset_name.text, flow),
                        )

                else:
                    index = i * columns + j
                    if index < len(elements):
                        dataset_card(elements[index], flow=flow)


def build_evaluation_page(flow: PromptMage):
    available_datasets = flow.data_store.backend.get_datasets()
    with ui.column().classes("items-center"):
        create_grid(available_datasets, flow=flow, columns=5)
