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
    graph_events = ""
    all_nodes = set()  # To keep track of all nodes
    nodes_with_outgoing_edges = set()  # To track nodes with outgoing edges
    id_to_step_name = {}  # Mapping of result_id to step name
    id_to_result = {}  # Mapping of result_id to result

    for result in execution_list:
        previous_ids = result["previous_result_ids"]
        current_id = result["current_result_id"]
        step_name = result["step"]

        # Store the mapping from id to step name
        id_to_step_name[current_id] = step_name

        # Store the mapping from id to result
        id_to_result[current_id] = result["results"]

        all_nodes.add(current_id)

        if previous_ids:
            for prev_id in previous_ids:
                diagram.append(f"    {prev_id} --> {current_id}")
                graph_events += (
                    f'click {prev_id} call emitEvent("graph_click", {prev_id})\n'
                )
                all_nodes.add(prev_id)
                nodes_with_outgoing_edges.add(prev_id)
        else:
            diagram.append(f"    start --> {current_id}")
            nodes_with_outgoing_edges.add("start")

    # Identify terminal nodes (nodes that do not have outgoing edges)
    terminal_nodes = all_nodes - nodes_with_outgoing_edges

    # Add 'END' for terminal nodes
    for node in terminal_nodes:
        graph_events += f'click {node} call emitEvent("graph_click", {node})\n'
        diagram.append(f"    {node} --> END")

    # Add labels for nodes using their step names
    for node_id, step_name in id_to_step_name.items():
        diagram.append(f"    {node_id}({step_name})")

    return "\n".join(diagram) + "\n" + graph_events, id_to_step_name, id_to_result


@ui.refreshable
def execution_graph(flow: PromptMage):
    with ui.dialog() as dialog, ui.card():
        ui.label("Execution Result will be shown here.")

    if flow.execution_results:
        for result in flow.execution_results:
            logger.info(
                f"{result.get('step')}, {result.get('current_result_id')}, {result.get('previous_result_ids')}, {result.get('results',{}).keys()}"
            )
        graph, id_to_step_name, id_to_result = render_mermaid_diagram(
            flow.execution_results
        )

        def node_dialog(id: str):
            dialog.clear()
            with dialog, ui.card().classes("w-512 h-128"):
                with ui.row().classes("w-full justify-between"):
                    ui.label(f"Result for step '{id_to_step_name[id]}'").classes(
                        "text-lg"
                    )
                    ui.space()
                    ui.button("Close", on_click=dialog.close)
                ui.markdown(
                    "\n\n".join(
                        f"{variable}:\n{result}"
                        for variable, result in id_to_result[id].items()
                    )
                )
            dialog.open()

        ui.mermaid(graph, config={"securityLevel": "loose"}).classes("w-2/3")
        ui.on("graph_click", lambda e: node_dialog(e.args))
        logger.info(graph)
    elif flow.is_running:
        ui.spinner("puff", size="xl")
    else:
        ui.label("No execution results available.")


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
