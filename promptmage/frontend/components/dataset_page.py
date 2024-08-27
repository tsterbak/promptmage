from nicegui import ui

from loguru import logger
from typing import List

from promptmage import PromptMage
from promptmage.run_data import RunData
from .styles import label_with_icon


# Function to build the rows for the table
def build_table_rows(runs, datapoints):
    return [
        {
            "step_run_id": run_data.step_run_id,
            "name": run_data.step_name,
            "rated": datapoint.rating if datapoint.rating else "Not rated",
        }
        for run_data, datapoint in zip(runs, datapoints)
    ]


def build_dataset_page(flow: PromptMage, dataset_id: str):
    # Get the dataset
    dataset = flow.data_store.backend.get_dataset(dataset_id)

    datapoints = flow.data_store.backend.get_datapoints(dataset_id)

    runs: List[RunData] = [
        flow.data_store.backend.get_data(datapoint.run_data_id)
        for datapoint in datapoints
    ]

    table = None
    progress_bar = None

    # side panel
    side_panel = (
        ui.element("div")
        .style(
            "position: fixed; top: 0; right: 0; width: 50%; height: 100%; transform: translateX(100%); transition: transform 0.3s ease; z-index: 1000; overflow-y: auto;"
        )
        .classes("bg-gray-100 dark:bg-slate-800")
    )

    # rating function
    def rate_run(datapoint, rating):
        flow.data_store.backend.rate_datapoint(datapoint.id, rating)

        # Update the datapoints and runs data after rating
        datapoints[:] = flow.data_store.backend.get_datapoints(dataset_id)
        runs[:] = [
            flow.data_store.backend.get_data(dp.run_data_id) for dp in datapoints
        ]
        # Refresh the table content
        table.rows = build_table_rows(runs, datapoints)
        table.update()

        # refresh progress
        progress = sum(datapoint.rating is not None for datapoint in datapoints) / len(
            datapoints
        )
        progress_bar.value = progress
        progress_bar.update()

    # Function to show the side panel with detailed information
    def show_side_panel(run_data: RunData):
        # Get the datapoint for the selected run
        datapoint = [
            datapoint
            for datapoint in datapoints
            if datapoint.run_data_id == run_data.step_run_id
        ][0]
        # Clear the side panel and update it with the new content
        side_panel.clear()
        with side_panel:
            ui.button(">>", on_click=hide_side_panel).style(
                "margin: 20px; margin-bottom: 0px; margin-top: 100px;"
            )
            with ui.card().style(
                "padding: 20px; margin-right: 20px; margin-top: 20px; margin-bottom: 20px; margin-left: 20px"
            ):
                # display run data
                with ui.row().classes("w-full"):
                    with ui.column().classes("gap-0"):
                        ui.label("Step name").classes("text-sm text-gray-500")
                        ui.label(f"{run_data.step_name}").classes("text-2xl")
                    ui.space()
                    with ui.column().classes("gap-0 items-center"):
                        ui.label("Status").classes("text-sm text-gray-500")
                        ui.chip(
                            f"{run_data.status}",
                            icon="",
                            color=f"{'green' if run_data.status == 'success' else 'red'}",
                        ).props("outline square")
                with ui.row().classes("w-full"):
                    with ui.column().classes("gap-0"):
                        label_with_icon(
                            "Execution time:", icon="hourglass_bottom"
                        ).classes("text-sm text-gray-500")
                        label_with_icon("Run At:", icon="o_schedule").classes(
                            "text-sm text-gray-500"
                        )
                        label_with_icon("Model:", icon="o_psychology").classes(
                            "text-sm text-gray-500"
                        )
                        label_with_icon("Step Run ID:", icon="o_info").classes(
                            "text-sm text-gray-500"
                        )
                        label_with_icon("Run ID:", icon="o_info").classes(
                            "text-sm text-gray-500"
                        )
                        label_with_icon("Rating:", icon="o_scale").classes(
                            "text-sm text-gray-500 pt-4"
                        )
                    with ui.column().classes("gap-0"):
                        ui.label(
                            f"{run_data.execution_time if run_data.execution_time else 0.0:.2f}s"
                        )
                        ui.label(f"{run_data.run_time[:19]}")
                        ui.label(f"{run_data.model}")
                        ui.label(f"{run_data.step_run_id}")
                        ui.label(f"{run_data.run_id}")
                        ui.label()
                        ui.chip(
                            f"{datapoint.rating if datapoint.rating else 'Not rated'}",
                            icon="",
                            color=f"{'grey' if not datapoint.rating else ('red' if datapoint.rating == -1 else 'green')}",
                        ).props("outline square")

                ui.label("Input Data:").classes("text-lg")
                for key, value in run_data.input_data.items():
                    ui.markdown(f"**{key}**")
                    ui.markdown(f"{value}")
                ui.label("Output Data:").classes("text-lg")
                try:
                    for key, value in run_data.output_data.items():
                        ui.markdown(f"**{key}**")
                        ui.markdown(f"{value}")
                except AttributeError:
                    ui.markdown(f"{run_data.output_data}")
                # rating buttons
                with ui.row():
                    ui.label("Rate this run:").classes("text-lg")
                    with ui.button_group():
                        ui.button(
                            icon="thumb_up",
                            on_click=lambda: rate_run(datapoint, 1),
                        )
                        ui.button(
                            icon="thumb_down",
                            on_click=lambda: rate_run(datapoint, -1),
                        )

        side_panel.style("transform:translateX(0%);")
        side_panel.update()

    # Function to hide the side panel
    def hide_side_panel():
        side_panel.clear()
        side_panel.style("transform:translateX(100%);")
        side_panel.update()

    # Function to download the data
    def download_data():
        import json

        logger.info("Downloading data")
        # Get the data
        data = [
            flow.data_store.backend.get_data(datapoint.run_data_id)
            for datapoint in datapoints
        ]
        # create the json file for export
        export_data = []
        for run_data, datapoint in zip(data, datapoints):
            export_data.append(
                {
                    "step_run_id": run_data.step_run_id,
                    "step_name": run_data.step_name,
                    "input_data": run_data.input_data,
                    "output_data": run_data.output_data,
                    "rating": datapoint.rating,
                }
            )
        # download the file
        ui.download(
            src=json.dumps(export_data, indent=4).encode("utf-8"),
            filename=f"{dataset.name}_data.json",
            media_type="application/json",
        )

    # Function to build the UI
    def build_ui():
        nonlocal table  # Access the outer-scope table variable
        nonlocal progress_bar  # Access the outer-scope progress_bar variable

        with ui.column().classes("w-2/5"):
            progress = sum(
                datapoint.rating is not None for datapoint in datapoints
            ) / len(datapoints)
            # header section
            with ui.card().classes("w-full"):
                with ui.row().classes("w-full"):
                    ui.label(f"Dataset name: {dataset.name}").classes("text-2xl")
                    ui.space()
                    ui.button(
                        "Delete",
                        on_click=lambda: flow.data_store.backend.delete_dataset(
                            dataset_id
                        ),
                    ).style("color: red;")
                    ui.button(
                        "Export",
                        on_click=download_data,
                    )
                ui.label(f"Number of datapoints: {len(datapoints)}").classes("text-lg")
                progress_bar = ui.linear_progress(
                    value=progress,
                    show_value=False,
                    size="20px",
                    color="primary",
                ).classes("w-full")

                # Create a table with clickable rows
                columns = [
                    {
                        "name": "step_run_id",
                        "label": "step_run_id",
                        "field": "step_run_id",
                    },
                    {
                        "name": "name",
                        "label": "name",
                        "field": "name",
                        "sortable": True,
                    },
                    {
                        "name": "rated",
                        "label": "rated",
                        "field": "rated",
                        "sortable": True,
                    },
                ]

                rows = build_table_rows(runs, datapoints)

                table = ui.table(
                    columns=columns,
                    rows=rows,
                    selection="multiple",
                    row_key="step_run_id",
                    pagination={
                        "rowsPerPage": 20,
                        "sortBy": "run_time",
                        "page": 1,
                        "descending": True,
                    },
                )

                table.add_slot(
                    "body-cell-rated",
                    """
                    <q-td key="rated" :props="props">
                        <q-badge :color="props.value === 'Not rated' ? 'grey' : (props.value === -1 ? 'red' : 'green')">
                            {{ props.value }}
                        </q-badge>
                    </q-td>
                    """,
                )

                def on_row_click(event):
                    selected_run_index = event.args[-2]["step_run_id"]
                    show_side_panel(
                        run_data=[
                            r for r in runs if r.step_run_id == selected_run_index
                        ][-1]
                    )

                table.on("rowClick", on_row_click)

    return build_ui
