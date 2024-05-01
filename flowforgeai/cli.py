"""This module contains the command line interface for the FlowForge package."""

import click
import uvicorn
from importlib import import_module
from pathlib import Path
import sys

from flowforgeai import FlowForge


@click.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--host", default="0.0.0.0", help="The host IP to run the FastAPI server on."
)
@click.option(
    "--port", default=8000, type=int, help="The port to run the FastAPI server on."
)
def serve(file_path, host, port):
    """Serve a FastAPI application containing a FlowForge instance from the given file."""
    sys.path.append(
        str(Path(file_path).parent.absolute())
    )  # Add the directory of the file to PYTHONPATH
    module_name = Path(file_path).stem
    module = import_module(module_name)

    # Find an instance of FlowForge in the module
    flow_instance = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, FlowForge):
            flow_instance = attr
            break

    if not flow_instance:
        raise ValueError("No FlowForge instance found in the module.")

    app = flow_instance.serve()

    # Run the FastAPI app
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    serve()
