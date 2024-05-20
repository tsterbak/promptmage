"""This module contains the command line interface for the PromptMage package."""

import click
import uvicorn

from promptmage.utils import get_flow
from promptmage.api import PromptMageAPI
from promptmage.frontend import PromptMageFrontend


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
    current_flow = get_flow(file_path)

    if not current_flow:
        raise ValueError("No PromptMage instance found in the module.")

    # create the FastAPI app
    app = PromptMageAPI(mage=current_flow).get_app()

    # create the frontend app
    frontend = PromptMageFrontend(mage=current_flow)
    frontend.init_from_api(app)

    # Run the applications
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    serve()
