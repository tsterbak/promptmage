import inspect
from fastapi import FastAPI, Path, Query
from fastapi.responses import HTMLResponse
from typing import Callable, Dict, Any


class FlowForge:
    def __init__(self, name: str):
        self.name: str = name
        self.steps: Dict = {}
        print(f"Initialized FlowForge with name: {name}")

    def step(self, name: str):
        # This is the outermost function taking the 'name' argument.
        def decorator(func):
            # This is the actual decorator.
            def wrapper(*args, **kwargs):
                # This is the wrapper function that will call the actual function.
                return func(*args, **kwargs)

            # Here we register the original function, not the wrapper, to maintain access to the original
            # function's signature which is important for FastAPI's routing and dependency injection.
            self.steps[name] = func

            # We return the wrapper here, but you might choose to return `func` if you don't need to modify behavior.
            return wrapper

        return decorator

    def create_endpoint_function(self, func, params):
        # Define the endpoint function using dynamic parameters
        async def endpoint(**kwargs):
            # Directly pass the keyword arguments to the function
            return func(**kwargs)

        return endpoint

    def serve(self) -> FastAPI:
        app = FastAPI()

        # create index endpoint
        @app.get("/")
        async def index():
            return HTMLResponse("<h1>Welcome to the FlowForge API</h1>")

        for step_name, func in self.steps.items():
            signature = inspect.signature(func)
            path = f"/api/{step_name}"
            params = []

            for name, param in signature.parameters.items():
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
