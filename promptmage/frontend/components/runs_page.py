from typing import List
from loguru import logger
from nicegui import ui, app
from slugify import slugify

from promptmage import PromptMage, RunData


def create_runs_view(mage: PromptMage):

    datasets = mage.data_store.backend.get_datasets()

    side_panel = ui.element("div").style(
        "position: fixed; top: 0; right: 0; width: 50%; height: 100%; background-color: #f0f0f0; transform: translateX(100%); transition: transform 0.3s ease; z-index: 1000; overflow-y: auto;"
    )
    # compare runs dialog
    compare_dialog = ui.dialog().props("full-width")

    def use_run_in_playground(step_run_id):
        app.storage.user["step_run_id"] = step_run_id
        ui.navigate.to(f"/{slugify(mage.name)}")

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
                ui.label(f"Run ID: {run_data.run_id}")
                ui.label(f"Step Name: {run_data.step_name}")
                ui.label(f"Status: {run_data.status}")
                ui.label(f"Run Time: {run_data.run_time}")
                ui.label(f"Prompt: {run_data.prompt}")
                ui.label("Input Data:").classes("text-lg")
                for key, value in run_data.input_data.items():
                    ui.markdown(f"**{key}**: {value}")
                ui.label("Output Data:").classes("text-lg")
                ui.markdown(f"{run_data.output_data}")
                with ui.row():
                    ui.button(
                        "Use in playground",
                        on_click=lambda: use_run_in_playground(run_data.step_run_id),
                    )
        side_panel.style("transform:translateX(0%);")
        side_panel.update()

    # Function to hide the side panel
    def hide_side_panel():
        side_panel.clear()
        side_panel.style("transform:translateX(100%);")
        side_panel.update()

    # rating function
    def rate_run(step_run_id, rating):
        logger.info(f"Rating run {step_run_id} with {rating}")
        ui.notify("Not implemented yet. Run rated successfully.")

    def build_ui():
        ui.label("Runs").classes("text-2xl")
        runs: List[RunData] = mage.get_run_data()

        def display_comparison():
            selected_runs = table.selected
            if len(selected_runs) < 2:
                ui.notify("Please select at least two runs to compare.")
                return
            if len(selected_runs) > 5:
                ui.notify("Please select at most five runs to compare.")
                return
            status_success = all([r["status"] == "success" for r in selected_runs])
            if not status_success:
                ui.notify("Please select only successful runs to compare.")
                return
            # check if all selected runs are from the same step
            step_names = set([r["name"] for r in selected_runs])
            if len(step_names) > 1:
                ui.notify("Please select runs from the same step to compare.")
                return
            compare_dialog.clear()
            with compare_dialog, ui.card():
                ui.label(f"Compare Runs for step {step_names.pop()}").classes(
                    "text-2xl"
                )
                with ui.row().style(
                    "display: flex; width: 100%; align-items: stretch;"
                ):
                    for run_data in selected_runs:
                        # get the results for the selected run
                        run: RunData = [
                            run
                            for run in runs
                            if run.step_run_id == run_data["step_run_id"]
                        ][0]
                        with ui.column().style("flex: 1;"):
                            with ui.card().style(
                                "flex-grow: 1; display: flex; flex-direction: column;"
                            ):
                                ui.label(f"step_run_id: {run_data['step_run_id']}")
                                ui.markdown(f"{run.output_data}")
                                with ui.button_group().style("margin-top: auto;"):
                                    ui.button(
                                        icon="thumb_up",
                                        on_click=lambda: rate_run(
                                            run.step_run_id, "up"
                                        ),
                                    )
                                    ui.button(
                                        icon="thumb_down",
                                        on_click=lambda: rate_run(
                                            run.step_run_id, "down"
                                        ),
                                    )

                ui.button("Close", on_click=compare_dialog.close)
            compare_dialog.open()

        def add_to_dataset():
            if dataset_select.value is None:
                ui.notify("Please select a dataset to add the runs to.")
                return
            dataset = datasets[dataset_select.value]
            selected_runs = table.selected
            for run in selected_runs:
                mage.data_store.backend.add_datapoint_to_dataset(
                    run["step_run_id"], dataset.id
                )
                logger.info(f"Added run {run['step_run_id']} to dataset {dataset.id}")
            ui.notify(
                f"Added {len(selected_runs)} runs to dataset {dataset.name} successfully."
            )

        # Main UI setup
        with ui.card().style("padding: 20px"):
            with ui.row():
                ui.button("Compare Runs", on_click=display_comparison).style(
                    "margin-bottom: 20px"
                )
                ui.button("Add to dataset", on_click=add_to_dataset).style(
                    "margin-bottom: 20px"
                )
                dataset_select = ui.select(
                    {idx: f"{d.name}-{d.id}" for idx, d in enumerate(datasets)},
                    value=None,
                )
            # Create a table with clickable rows
            columns = [
                {
                    "name": "run_id",
                    "label": "run_id",
                    "field": "run_id",
                },
                {"name": "step_run_id", "label": "step_run_id", "field": "step_run_id"},
                {"name": "name", "label": "name", "field": "name", "sortable": True},
                {
                    "name": "status",
                    "label": "status",
                    "field": "status",
                    "sortable": True,
                },
                {
                    "name": "run_time",
                    "label": "run_time",
                    "field": "run_time",
                    "sortable": True,
                },
            ]

            rows = [
                {
                    "run_id": run_data.run_id,
                    "step_run_id": run_data.step_run_id,
                    "name": run_data.step_name,
                    "status": run_data.status,
                    "run_time": run_data.run_time,
                }
                for run_data in runs
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
                "body-cell-status",
                """
                <q-td key="status" :props="props">
                    <q-badge :color="props.value === 'failed' ? 'red' : 'green'">
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
