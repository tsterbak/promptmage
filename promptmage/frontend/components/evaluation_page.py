from nicegui import ui
from typing import List
from slugify import slugify
from loguru import logger

from promptmage import PromptMage


def build_evaluation_page(flow: PromptMage):
    available_datasets = []

    def get_datasets():
        nonlocal available_datasets
        available_datasets = flow.data_store.backend.get_datasets()

    get_datasets()
    columns: int = 5

    def dataset_card(dataset, flow):
        datapoints = flow.data_store.backend.get_datapoints(dataset.id)
        is_done = (
            all([dp.rating is not None for dp in datapoints]) and len(datapoints) > 0
        )
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
                    ui.label("Description")
                    ui.label("Created at")
                    ui.label("Datapoints")
                    ui.label("Progress")
                    ui.label("Average rating")
                with ui.column():
                    ui.label(
                        f"{dataset.description if dataset.description else 'No description'}"
                    )
                    ui.label(f"{dataset.created}")
                    ui.label(f"{len(datapoints)}")
                    if len(datapoints) == 0:
                        ui.label("0%")
                        ui.label("N/A")
                    else:
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

    def create_dataset(name: str, description: str, flow: PromptMage):
        """Create a new dataset.

        Args:
            name (str): The name of the dataset.
            description (str): The description of the dataset.
            flow (PromptMage): The PromptMage instance.
        """
        logger.info(f"Creating dataset: {name}")
        try:
            flow.data_store.backend.create_dataset(name, description)
            ui.notify(f"Dataset {name} created.")
            get_datasets()
            create_grid.refresh()
        except Exception as e:
            logger.error(f"Error creating dataset: {e}")

    def delete_dataset(dataset_id: str, flow: PromptMage):
        flow.data_store.backend.delete_dataset(dataset_id)
        logger.info(f"Deleted dataset: {dataset_id}")
        get_datasets()
        create_grid.refresh()

    def create_new_dataset_dialog(flow: PromptMage):
        # create new dataset dialog
        dialog = ui.dialog()
        with dialog, ui.card():
            ui.label("Create new dataset").classes("text-2xl")
            # fields
            name = ui.input(
                label="Name",
                placeholder="Enter the name of the dataset",
                validation={
                    "Name must be shorter than 100 characters!": lambda value: len(
                        value
                    )
                    < 100
                },
            )
            description = ui.textarea(
                label="Description",
                placeholder="Enter the description of the dataset",
                validation={
                    "Description must be shorter than 1000 characters!": lambda value: len(
                        value
                    )
                    < 1000
                },
            ).props("clearable")
            # final buttons
            with ui.row().classes("justify-end"):
                ui.button(
                    "Create",
                    on_click=lambda: create_dataset(
                        name=name.value, description=description.value, flow=flow
                    ),
                )
                ui.button("Close", on_click=dialog.close)
        return dialog

    @ui.refreshable
    def create_grid():
        new_dataset_dialog = create_new_dataset_dialog(flow)
        available_datasets.insert(0, None)
        rows = len(available_datasets) // columns + (
            1 if len(available_datasets) % columns > 0 else 0
        )
        if rows == 0:
            rows = 1
        for i in range(rows):
            with ui.row().classes("justify-center"):
                for j in range(columns):
                    if i == j == 0:
                        with ui.card().style("padding: 20px; margin: 10px;"):
                            ui.button(
                                "Create dataset",
                                icon="add",
                                on_click=lambda: new_dataset_dialog.open(),
                            )

                    else:
                        index = i * columns + j
                        if index < len(available_datasets):
                            dataset_card(available_datasets[index], flow=flow)

    with ui.column().classes("items-center"):
        create_grid()
