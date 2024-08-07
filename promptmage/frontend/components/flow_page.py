from nicegui import ui

from promptmage import PromptMage
from promptmage.step import MageStep
from .main_runner import create_main_runner
from .step_runner import create_function_runner


@ui.refreshable
def execution_graph(flow: PromptMage):
    graph = "graph TD;\n"
    graph_events = ""
    for step in flow.execution_results:
        if step.get("next_step") is None:
            graph += f'{step.get("step")} --> END;\n'
        else:
            graph += f'{step.get("step")} --> {step.get("next_step")};\n'
        graph_events += f'click {step.get("step")} call emitEvent("graph_click", "You clicked {step.get("step")}-{step.get("step_id")}!")\n'
    ui.mermaid(graph + graph_events, config={"securityLevel": "loose"})
    ui.on("graph_click", lambda e: ui.notify(e.args))


def build_flow_page(flow: PromptMage):
    with ui.row().classes("w-full gap-0"):
        with ui.column().classes("w-1/2 items-center"):
            # Create a card for the mage
            with ui.card().classes("w-full"):
                ui.label(f"Flow: {flow.name}").classes("text-xl")
                with create_main_runner(flow, execution_graph):
                    # Create a card for each step
                    with ui.column().classes("w-full"):
                        step: MageStep
                        for step in flow.steps.values():
                            create_function_runner(step)()
        # Create a card for the execution graph
        with ui.column().classes("w-1/2 items-center pl-4"):
            with ui.card().classes("w-full"):
                ui.label("Execution graph").classes("text-xl")
                execution_graph(flow)
