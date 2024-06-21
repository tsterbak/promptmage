from promptmage import PromptMage
from nicegui import ui, app


def create_runs_view(mage: PromptMage):

    side_panel = ui.element("div").style(
        "position: fixed; top: 0; right: 0; width: 50%; height: 100%; background-color: #f0f0f0; transform: translateX(100%); transition: transform 0.3s ease; z-index: 1000; overflow-y: auto;"
    )

    def use_run_in_playground(step_run_id):
        app.storage.user["step_run_id"] = step_run_id
        ui.navigate.to("/")

    # Function to show the side panel with detailed information
    def show_side_panel(run_data):
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
                ui.label("Input Data:")
                for key, value in run_data.input_data.items():
                    ui.markdown(f"**{key}**: {value}")
                ui.label(f"Output Data: {run_data.output_data}")
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

    def build_ui():
        ui.label("Runs").classes("text-2xl")
        runs = mage.get_run_data()

        # Main UI setup
        with ui.card().style("padding: 20px"):
            # Create a table with clickable rows
            columns = [
                {"name": "run_id", "label": "run_id", "field": "run_id"},
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
