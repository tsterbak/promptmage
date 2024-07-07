from nicegui import ui

from promptmage import PromptMage
from promptmage.step import MageStep
from .main_runner import create_main_runner
from .step_runner import create_function_runner


def build_flow_page(flow: PromptMage):
    with ui.row().style("flex-wrap: wrap;"):
        # Create a card for the mage
        with ui.column().style("flex-wrap: wrap;"):
            with ui.card():
                ui.label("Run all steps")
                create_main_runner(flow)()
        # Create a card for each step
        with ui.column().style("flex-wrap: wrap;"):
            step: MageStep
            for step in flow.steps.values():
                create_function_runner(step)()
