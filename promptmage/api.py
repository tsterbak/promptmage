"""This module contains the API for the PromptMage package."""

import inspect
import pkg_resources
from pathlib import Path

from fastapi import FastAPI, Path, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


from promptmage import PromptMage


class PromptMageAPI:
    """A class that creates a FastAPI application to serve a PromptMage instance."""

    def __init__(self, mage: PromptMage):
        self.mage = mage

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

        # create index endpoint
        @app.get("/")
        async def index():
            return HTMLResponse(
                """<h1>Welcome to the PromptMage</h1>"""
                """<h2>To see the API docs 📖, go to <a href='/docs'>/docs</a></h2>"""
                """<h2>To access the API 🔮, go to <a href='/api'>/api</a></h2>"""
                """<h2>To access the GUI 🧙, go to <a href='/gui'>/gui</a></h2>"""
            )

        @app.get("/api")
        async def root():
            return HTMLResponse("<h1>Welcome to the PromptMage API</h1>")

        @app.get("/api/prompts")
        async def list_prompts():
            return self.mage.prompt_store.get_prompts()

        @app.get("/api/data")
        async def list_data():
            return self.mage.data_store.get_all_data()

        # create the endpoints for each step
        step_list = []
        for step_name, step in self.mage.steps.items():
            signature = inspect.signature(step.func)
            path = f"/api/{step_name}"
            params, path_variables = self._parameters_from_signature(signature)
            path += path_variables

            # Update the signature for the endpoint function
            new_signature = signature.replace(parameters=params)
            endpoint_func = self.create_endpoint_function(step.func, new_signature)
            setattr(
                endpoint_func, "__signature__", new_signature
            )  # Update the signature for FastAPI to recognize

            # Add the route to FastAPI
            app.add_api_route(path, endpoint_func, methods=["GET"])
            step_list.append({"name": step_name, "path": path})

        # create an endpoint to run the full dependency graph of the flow
        run_function = self.mage.get_run_function()
        signature = inspect.signature(run_function)
        path = "/api/run_flow"
        params, path_variables = self._parameters_from_signature(signature)
        path += path_variables
        new_signature = signature.replace(parameters=params)
        endpoint_func = self.create_endpoint_function(run_function, new_signature)
        setattr(endpoint_func, "__signature__", new_signature)
        app.add_api_route(path, endpoint_func, methods=["GET"])

        # add a route to list all available steps with their names and input variables
        @app.get("/api/steps")
        async def list_steps():
            return step_list

        static_files_path = pkg_resources.resource_filename("promptmage", "static/")
        app.mount(
            "/static/",
            StaticFiles(directory=static_files_path, html=True),
            name="static",
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

    def create_endpoint_function(self, func, params):
        # Define the endpoint function using dynamic parameters
        async def endpoint(*args, **kwargs):
            # Directly pass the keyword arguments to the function
            return func(*args, **kwargs)

        return endpoint
