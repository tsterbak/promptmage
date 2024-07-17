from nicegui import ui

from promptmage import PromptMage
from promptmage.step import MageStep
from .main_runner import create_main_runner
from .step_runner import create_function_runner


def build_flow_page(flow: PromptMage):
    with ui.row().classes("w-full gap-0"):
        # Create a card for the mage
        with ui.column().classes("w-1/3 pr-5"):
            with ui.card().classes("w-full"):
                ui.label(f"{flow.name}").classes("text-xl")
                ui.label("Run all steps")
                create_main_runner(flow)()
        # Create a card for each step
        with ui.column().classes("w-2/3"):
            step: MageStep
            for step in flow.steps.values():
                create_function_runner(step)()
