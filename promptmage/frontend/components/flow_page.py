from nicegui import ui
from loguru import logger

from promptmage import PromptMage
from promptmage.step import MageStep
from .main_runner import create_main_runner
from .step_runner import create_function_runner


def render_mermaid_diagram(execution_list: list) -> str:
    """
    Generate a Mermaid diagram from the self.execution_results.

    Returns:
        str: The Mermaid diagram code.
    """
    diagram = ["graph TD"]
    all_nodes = set()  # To keep track of all nodes
    nodes_with_outgoing_edges = set()  # To track nodes with outgoing edges
    id_to_step_name = {}  # Mapping of result_id to step name

    for result in execution_list:
        previous_ids = result["previous_result_ids"]
        current_id = result["current_result_id"]
        step_name = result["step"]

        # Store the mapping from id to step name
        id_to_step_name[current_id] = step_name

        all_nodes.add(current_id)

        if previous_ids:
            for prev_id in previous_ids:
                diagram.append(f"    {prev_id} --> {current_id}")
                all_nodes.add(prev_id)
                nodes_with_outgoing_edges.add(prev_id)
        else:
            diagram.append(f"    start --> {current_id}")
            nodes_with_outgoing_edges.add("start")

    # Identify terminal nodes (nodes that do not have outgoing edges)
    terminal_nodes = all_nodes - nodes_with_outgoing_edges

    # Add 'END' for terminal nodes
    for node in terminal_nodes:
        diagram.append(f"    {node} --> END")

    # Add labels for nodes using their step names
    for node_id, step_name in id_to_step_name.items():
        diagram.append(f"    {node_id}({step_name})")

    return "\n".join(diagram)


@ui.refreshable
def execution_graph(flow: PromptMage):
    if flow.execution_results:
        logger.info(flow.execution_results)
        graph = render_mermaid_diagram(flow.execution_results)
        #    graph_events += f'click {step.get("step_id")} call emitEvent("graph_click", "You clicked {step.get("step")} with ID {step.get("current_result_id")}!")\n'
        # graph += f'{step.get("current_result_id")}[{step.get("step")}] --> END;\n'
        ui.mermaid(graph, config={"securityLevel": "loose"})
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
