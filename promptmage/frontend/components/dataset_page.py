from nicegui import ui

from loguru import logger
from typing import List

from promptmage import PromptMage
from promptmage.run_data import RunData


def build_dataset_page(flow: PromptMage, dataset_id: str):
    dataset = flow.data_store.backend.get_dataset(dataset_id)
    ui.label(f"Dataset name: {dataset.name} - id: {dataset_id}").classes("text-2xl")

    datapoints = flow.data_store.backend.get_datapoints(dataset_id)

    side_panel = ui.element("div").style(
        "position: fixed; top: 0; right: 0; width: 50%; height: 100%; background-color: #f0f0f0; transform: translateX(100%); transition: transform 0.3s ease; z-index: 1000; overflow-y: auto;"
    )
    # compare runs dialog
    compare_dialog = ui.dialog().props("full-width")

    # Function to show the side panel with detailed information
    def show_side_panel(run_data: RunData):
        side_panel.clear()
        with side_panel:
            ui.button(">>", on_click=hide_side_panel).style(
                "margin: 20px; margin-bottom: 0px; margin-top: 100px;"
            )
            with ui.card().style(
                "padding: 20px; margin-right: 20px; margin-top: 20px; margin-bottom: 20px; margin-left: 20px"
            ):
                # display run data
                ui.label(f"Step Run ID: {run_data.step_run_id}")
                ui.label(f"Step Name: {run_data.step_name}")
                ui.label("Input Data:").classes("text-lg")
                for key, value in run_data.input_data.items():
                    ui.markdown(f"**{key}**: {value}")
                ui.label("Output Data:").classes("text-lg")
                ui.markdown(f"{run_data.output_data}")
                # rating buttons
                with ui.button_group():
                    datapoint = [
                        datapoint
                        for datapoint in datapoints
                        if datapoint.run_data_id == run_data.step_run_id
                    ][0]
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

    # rating function
    def rate_run(datapoint, rating):
        flow.data_store.backend.rate_datapoint(datapoint.id, rating)

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
        runs: List[RunData] = [
            flow.data_store.backend.get_data(datapoint.run_data_id)
            for datapoint in datapoints
        ]

        # Main UI setup
        with ui.card().style("padding: 20px"):
            with ui.row().classes("justify-end"):
                ui.button("Export", on_click=download_data).style("margin-bottom: 20px")
            # Create a table with clickable rows
            columns = [
                {"name": "step_run_id", "label": "step_run_id", "field": "step_run_id"},
                {"name": "name", "label": "name", "field": "name", "sortable": True},
                {
                    "name": "rated",
                    "label": "rated",
                    "field": "rated",
                    "sortable": True,
                },
            ]

            rows = [
                {
                    "step_run_id": run_data.step_run_id,
                    "name": run_data.step_name,
                    "rated": eval_data.rating if eval_data.rating else "Not rated",
                }
                for run_data, eval_data in zip(runs, datapoints)
            ]

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
                    <q-badge :color="props.value === 'Not rated' ? 'red' : 'green'">
                        {{ props.value }}
                    </q-badge>
                </q-td>
                """,
            )

            def on_row_click(event):
                selected_run_index = event.args[-2]["step_run_id"]
                show_side_panel(
                    run_data=[r for r in runs if r.step_run_id == selected_run_index][
                        -1
                    ]
                )

            table.on("rowClick", on_row_click)

    return build_ui
