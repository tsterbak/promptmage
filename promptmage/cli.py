"""This module contains the command line interface for the PromptMage package."""

import json
import click
import uvicorn
from pathlib import Path
from loguru import logger

from promptmage import __version__, title
from promptmage.utils import get_flows
from promptmage.api import PromptMageAPI
from promptmage.frontend import PromptMageFrontend
from promptmage.storage import SQLiteDataBackend, SQLitePromptBackend


@click.group()
def promptmage():
    """Promptmage CLI"""
    pass


@click.command()
def version():
    """Print the version of the PromptMage package."""
    click.echo(f"PromptMage version: {__version__}")


@click.command()
@click.argument(
    "file_path",
    type=click.Path(
        exists=True,
    ),
)
@click.option("--host", default="0.0.0.0", help="The host IP to run the server on.")
@click.option("--port", default=8000, type=int, help="The port to run the server on.")
@click.option(
    "--browser",
    is_flag=True,
    help="Open the browser after starting the server.",
    default=False,
)
def run(file_path: str, host: str, port: int, browser: bool):
    """Serve the application containing a PromptMage instance from the given file.

    Args:
        file_path (str): The path to the file containing the PromptMage instance.
        host (str): The host IP to run the FastAPI server on.
        port (int): The port to run the FastAPI server on.
        browser (bool): Whether to open the browser after starting the server.
    """
    logger.info(f"\nWelcome to\n{title}")
    logger.info(f"Running PromptMage version {__version__} from {file_path}")
    # create the .promptmage directory to store all the data
    dirPath = Path(".promptmage")
    dirPath.mkdir(mode=0o777, parents=False, exist_ok=True)

    # get the available flows from the source file
    available_flows = get_flows(file_path)

    if not available_flows:
        raise ValueError("No PromptMage instance found in the module.")

    # create the FastAPI app
    app = PromptMageAPI(flows=available_flows).get_app()

    # create the frontend app
    frontend = PromptMageFrontend(flows=available_flows)
    frontend.init_from_api(app)

    # Run the applications
    if browser:
        import webbrowser

        url = f"http://localhost:{port}"
        webbrowser.open_new_tab(url)
    uvicorn.run(app, host=host, port=port, log_level="info")


@click.command()
@click.option("--runs", "runs", default=False, help="Export runs.", flag_value=True)
@click.option(
    "--prompts", "prompts", default=False, help="Export prompts.", flag_value=True
)
@click.option(
    "--filename",
    default="promptmage",
    help="The name of the file to export the data to.",
)
def export(runs: bool = False, prompts: bool = False, filename: str = "promptmage"):
    """Export the run data and prompts from the PromptMage instance to json.

    Args:
        runs (bool): Whether to export the run data.
        prompts (bool): Whether to export the prompts.
        filename (str): The name of the file to export the data to.
    """
    if runs:
        click.echo("Exporting runs...")
        data_store = SQLiteDataBackend()
        run_data = data_store.get_all_data()

        with open(f"{filename}_runs.json", "w") as f:
            json.dump([run for run in run_data.values()], f)

    if prompts:
        click.echo("Exporting prompts...")
        prompt_store = SQLitePromptBackend()
        prompts = prompt_store.get_prompts()

        with open(f"{filename}_prompts.json", "w") as f:
            json.dump([prompt.to_dict() for prompt in prompts], f)

    if not runs and not prompts:
        click.echo("No data to export.")
    else:
        click.echo("Export complete.")


promptmage.add_command(version)
promptmage.add_command(run)
promptmage.add_command(export)


if __name__ == "__main__":
    promptmage()
