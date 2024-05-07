import inspect
import tempfile
import textwrap
from functools import partial
from typing import Callable, Dict, Any

# API imports
from fastapi import FastAPI, Path, Query
from fastapi.responses import HTMLResponse

# Local imports
from .prompt import Prompt


class FlowForge:
    def __init__(self, name: str):
        self.name: str = name
        self.steps: Dict = {}
        print(f"Initialized FlowForge with name: {name}")

    def step(self, name: str, prompt_id: str = None):
        """Decorator to add a step to the FlowForge instance.

        Args:
            name (str): The name of the step.
            prompt_id (str, optional): The ID of the prompt to use for this step. Defaults to None.
        """
        # Load the prompt if provided
        prompt = Prompt(prompt_id) if prompt_id else None

        def decorator(func):
            # This is the actual decorator.
            def wrapper(*args, **kwargs):
                if prompt:
                    kwargs["prompt"] = prompt
                    return func(*args, **kwargs)
                return func(*args, **kwargs)

            if prompt:
                self.steps[name] = partial(func, prompt=prompt)
            else:
                self.steps[name] = func
            return wrapper

        return decorator

    def create_endpoint_function(self, func, params):
        # Define the endpoint function using dynamic parameters
        async def endpoint(*args, **kwargs):
            # Directly pass the keyword arguments to the function
            return func(*args, **kwargs)

        return endpoint

    def serve_api(self) -> FastAPI:
        """Create a FastAPI application to serve the FlowForge instance."""
        app = FastAPI()

        # create index endpoint
        @app.get("/")
        async def index():
            return HTMLResponse("<h1>Welcome to the FlowForge API</h1>")

        # create the endpoints for each step
        for step_name, func in self.steps.items():
            signature = inspect.signature(func)
            path = f"/api/{step_name}"
            params = []

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

            # Update the signature for the endpoint function
            new_signature = signature.replace(parameters=params)
            endpoint_func = self.create_endpoint_function(func, new_signature)
            setattr(
                endpoint_func, "__signature__", new_signature
            )  # Update the signature for FastAPI to recognize

            # Add the route to FastAPI
            app.add_api_route(path, endpoint_func, methods=["GET"])

        return app

    def serve_frontend(self, app_function: Callable) -> str:
        # Extract the function source code using inspect
        app_function_code = inspect.getsource(app_function)
        app_function_code = textwrap.dedent(app_function_code)

        # Create the temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
            # Write the function source code into the temp file
            tmp_file.write("import streamlit as st\n".encode())
            tmp_file.write(app_function_code.encode())

            # Write the call to the function within the main block
            tmp_file.write(
                f"\n\nif __name__ == '__main__':\n    {app_function.__name__}()\n".encode()
            )
            tmp_file_name = tmp_file.name

        return tmp_file_name
