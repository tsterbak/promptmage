"""This module contains the command line interface for the PromptMage package."""

import click
import asyncio
import uvicorn
import multiprocessing

from promptmage.utils import get_flow


def run_fastapi(app, host, port):
    # Run the FastAPI app
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass


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
    app = current_flow.get_api()

    # create the frontend app

    # Run the FastAPI app
    fastapi_process = multiprocessing.Process(
        target=run_fastapi, args=(app, host, port)
    )

    # Start both processes
    fastapi_process.start()

    # Wait for both processes to finish
    try:
        fastapi_process.join()
    except KeyboardInterrupt:
        fastapi_process.terminate()
        fastapi_process.join()


if __name__ == "__main__":
    serve()
