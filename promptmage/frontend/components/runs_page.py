from promptmage.storage.data_store import DataStore

from nicegui import ui


def create_runs_view(data_store: DataStore):

    def build_ui():
        with ui.column():
            ui.label("Runs")
            runs = data_store.get_all_data()
            for run_id, run_data in runs.items():
                with ui.card():
                    with ui.expansion(
                        f"Run {run_id} of step \"{run_data['step_name']}\""
                    ).classes("w-full"):
                        ui.label(f"Run time: {run_data['run_time']}")
                        ui.label(f"Prompt: {run_data['prompt']}")
                        ui.label(f"Input data: {run_data['input_data']}")
                        ui.label(f"Output data: {run_data['output_data']}")
                    ui.update()

    return build_ui
