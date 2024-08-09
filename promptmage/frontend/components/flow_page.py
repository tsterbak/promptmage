from nicegui import ui
from loguru import logger

from promptmage import PromptMage
from promptmage.step import MageStep
from .main_runner import create_main_runner
from .step_runner import create_function_runner


@ui.refreshable
def execution_graph(flow: PromptMage):
    if flow.execution_results:
        logger.info(flow.execution_results)
        graph = "graph TD;\n"
        graph_events = ""
        for step in flow.execution_results:
            if step.get("previous_result_id") is None:
                graph += f'START --> {step.get("result_id")}[{step.get("step")}];\n'
            else:
                graph += f'{step.get("previous_result_id")}[{step.get("previous_step")}] --> {step.get("result_id")}[{step.get("step")}];\n'
            graph_events += f'click {step.get("result_id")} call emitEvent("graph_click", "You clicked {step.get("step")} with ID {step.get("id")}!")\n'
        graph += f'{step.get("result_id")}[{step.get("step")}] --> END;\n'
        ui.mermaid(graph + graph_events, config={"securityLevel": "loose"})
        ui.on("graph_click", lambda e: ui.notify(e.args))
        logger.info(graph)
    else:
        ui.spinner("puff", size="xl")


def build_flow_page(flow: PromptMage):
    with ui.row().classes("w-full gap-0"):
        with ui.splitter().classes("w-full") as splitter:
            with splitter.before:
                with ui.column().classes("w-full items-center"):
                    # Create a card for the mage
                    with ui.card().classes("w-full"):
                        ui.label(f"Flow: {flow.name}").classes("text-xl")
                        with create_main_runner(flow, execution_graph):
                            # Create a card for each step
                            with ui.column().classes("w-full"):
                                step: MageStep
                                for step in flow.steps.values():
                                    create_function_runner(step)()
            with splitter.after:
                # Create a card for the execution graph
                with ui.column().classes("w-full items-center pl-4"):
                    with ui.card().classes("w-full items-center"):
                        ui.label("Execution graph").classes("text-xl")
                        execution_graph(flow)
