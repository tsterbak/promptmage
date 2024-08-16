"""Frontend module for PromptMage."""

from fastapi import FastAPI
from nicegui import ui
from typing import List
from slugify import slugify

from promptmage import PromptMage

from .components import theme
from .components.runs_page import create_runs_view
from .components.prompts_page import create_prompts_view
from .components.overview_page import build_overview_page
from .components.flow_page import build_flow_page
from .components.evaluation_page import build_evaluation_page
from .components.dataset_page import build_dataset_page


class PromptMageFrontend:
    """A class that creates a frontend for a PromptMage instance."""

    def __init__(self, flows: List[PromptMage]):
        self.flows = flows
        self.flows_dict = {slugify(flow.name): flow for flow in flows}
        self.current_flow = self.flows[0]

    def init_from_api(self, fastapi_app: FastAPI) -> None:
        """Initialize the frontend from a FastAPI application."""

        @ui.page("/", title="PromptMage")
        def main_page():
            with theme.frame(
                "Welcome to the PromptMage", flow_name=slugify(self.current_flow.name)
            ):
                build_overview_page(self.flows)

        @ui.page("/{flow_name}", title="PromptMage - Flow")
        def flow_page(flow_name: str):
            self.current_flow = self.flows_dict[flow_name]
            with theme.frame(f"Playground {flow_name}", flow_name=flow_name):
                build_flow_page(self.flows_dict[flow_name])

        @ui.page("/runs/{flow_name}", title="PromptMage - Runs")
        def runs_page(flow_name: str):
            self.current_flow = self.flows_dict[flow_name]
            with theme.frame(f"Runs Overview - {flow_name}", flow_name=flow_name):
                create_runs_view(self.current_flow)()

        @ui.page("/prompts/{flow_name}", title="PromptMage - Prompts")
        def prompts_page(flow_name: str):
            self.current_flow = self.flows_dict[flow_name]
            with theme.frame(f"Prompts Overview _ {flow_name}", flow_name=flow_name):
                create_prompts_view(self.current_flow)()

        @ui.page("/evaluation/{flow_name}", title="PromptMage - Evaluation")
        def evaluation_page(flow_name: str):
            self.current_flow = self.flows_dict[flow_name]
            with theme.frame(f"Evaluation - {flow_name}", flow_name=flow_name):
                build_evaluation_page(self.current_flow)

        @ui.page(
            "/evaluation/{flow_name}/{dataset_id}",
            title="PromptMage - Evaluation Dataset",
        )
        def evaluation_dataset_page(flow_name: str, dataset_id: str):
            self.current_flow = self.flows_dict[flow_name]
            with theme.frame(
                f"Evaluation - {flow_name} - {dataset_id}", flow_name=flow_name
            ):
                build_dataset_page(self.current_flow, dataset_id)()

        ui.run_with(
            fastapi_app,
            mount_path="/gui",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
            storage_secret="pick your private secret here",  # NOTE setting a secret is optional but allows for persistent storage per user
            dark=False,
            favicon="🧙",
        )
