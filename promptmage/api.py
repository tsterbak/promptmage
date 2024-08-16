"""This module contains the API for the PromptMage package."""

import inspect
import pkg_resources
from loguru import logger
from typing import List, Callable
from pathlib import Path
from pydantic import BaseModel
from slugify import slugify

from fastapi import FastAPI, Path, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


from promptmage import PromptMage


class PromptMageAPI:
    """A class that creates a FastAPI application to serve a PromptMage instance."""

    def __init__(self, flows: List[PromptMage]):
        self.flows = flows
        self.mage = flows[0]

    def get_app(self) -> FastAPI:
        """Create a FastAPI application to serve the PromptMage instance."""
        app = FastAPI(
            title=f"PromptMage API: {self.mage.name}", description="API for PromptMage."
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        static_files_path = pkg_resources.resource_filename("promptmage", "static/")
        app.mount(
            "/static/",
            StaticFiles(directory=static_files_path, html=True),
            name="static",
        )

        # create index endpoint
        @app.get("/")
        async def index():
            return HTMLResponse(
                """<h1>Welcome to the PromptMage</h1>"""
                """<h2>To see the API docs 📖, go to <a href='/docs'>/docs</a></h2>"""
                """<h2>To access the API 🔮, go to <a href='/api'>/api</a></h2>"""
                """<h2>To access the GUI 🧙, go to <a href='/gui'>/gui</a></h2>"""
            )

        # create index API endpoint
        @app.get("/api")
        async def root():
            flow_names_to_slug = {flow.name: slugify(flow.name) for flow in self.flows}
            flow_message = "<h2>Available flows:</h2>"
            for name, slug in flow_names_to_slug.items():
                flow_message += f"<br><a href='/api/{slug}'>{name}</a>"
            return HTMLResponse(
                f"<h1>Welcome to the PromptMage API</h1><p>{flow_message}</p>"
            )

        # create an endpoint list of all available flows
        @app.get("/api/flows")
        async def list_flows():
            flow_names_to_slug = {flow.name: slugify(flow.name) for flow in self.flows}
            return flow_names_to_slug

        # create the endpoints for each flow
        for flow in self.flows:

            @app.get(f"/api/{slugify(flow.name)}/prompts", tags=[flow.name])
            async def list_prompts():
                return self.mage.prompt_store.get_prompts()

            @app.get(f"/api/{slugify(flow.name)}/data", tags=[flow.name])
            async def list_data():
                return self.mage.data_store.get_all_data()

            # add a route to list all available steps with their names and input variables
            @app.get(f"/api/{slugify(flow.name)}/steps", tags=[flow.name])
            async def list_steps():
                return step_list

            # create the endpoints for each step
            step_list = []
            for step_name, step in self.mage.steps.items():
                signature = inspect.signature(step.func)
                path = f"/api/{slugify(flow.name)}/{step_name}"
                params, path_variables = self._parameters_from_signature(signature)
                # TODO: not use path variables but build a request body dynamically
                path += path_variables

                # Update the signature for the endpoint function
                new_signature = signature.replace(parameters=params)
                endpoint_func = self.create_endpoint_function(step.execute)
                setattr(
                    endpoint_func, "__signature__", new_signature
                )  # Update the signature for FastAPI to recognize

                # Add the route to FastAPI
                app.add_api_route(
                    path,
                    endpoint_func,
                    methods=["GET"],
                    tags=[flow.name],
                    response_model=EndpointResponse,
                )
                step_list.append({"name": step_name, "path": path})

            # create an endpoint to run the full dependency graph of the flow
            run_function = self.mage.get_run_function()
            signature = inspect.signature(run_function)
            path = f"/api/{slugify(flow.name)}/run_flow"
            params, path_variables = self._parameters_from_signature(signature)
            path += path_variables
            new_signature = signature.replace(parameters=params)
            endpoint_func = self.create_endpoint_function(run_function)
            setattr(endpoint_func, "__signature__", new_signature)
            app.add_api_route(
                path,
                endpoint_func,
                methods=["GET"],
                response_model=EndpointResponse,
                tags=[flow.name],
            )

        return app

    def _parameters_from_signature(self, signature):
        params = []
        path = ""
        for name, param in signature.parameters.items():
            # ignore prompt parameter
            if name == "prompt":
                continue
            if param.default is inspect.Parameter.empty:
                # Assume required parameters are path parameters
                new_param = inspect.Parameter(
                    name,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=Path(..., description=f"Path parameter `{name}`"),
                    annotation=param.annotation,
                )
                path += f"/{{{name}}}"  # Add to the path
            else:
                # Parameters with defaults are query parameters
                new_param = inspect.Parameter(
                    name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Query(
                        param.default, description=f"Query parameter `{name}`"
                    ),
                    annotation=param.annotation,
                )
            params.append(new_param)
        return params, path

    def create_endpoint_function(self, func: Callable) -> Callable:
        # Define the endpoint function using dynamic parameters
        async def endpoint(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return EndpointResponse(
                    name=f"{func.__name__}",
                    status=200,
                    message="Success",
                    result=str(result),
                )
            except Exception as e:
                logger.info(f"Failed to call {func.__name__}")
                return EndpointResponse(
                    name=f"{func.__name__}",
                    status=500,
                    message=f"Error when calling {func.__name__}: {e}",
                )

        return endpoint


class EndpointResponse(BaseModel):
    name: str
    status: int = 500
    message: str = "Internal Server Error"
    result: str | List[str] | None = None
