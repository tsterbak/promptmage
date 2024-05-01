"""This module contains the command line interface for the flowforgeai package."""

import click


def help():
    """Show the help message for the CLI."""
    print("Usage: flowforge <entrypoint>")
    print()
    print("Available entrypoints:")
    print("  help: Show this help message")
    print("  run: Run the flowforgeai package")


def run():
    """Run the flowforgeai package."""
    print("Running the flowforge package")


@click.command()
@click.argument("entrypoint", type=str, default="help")
def main(entrypoint: str):
    if entrypoint == "help":
        help()
    elif entrypoint == "run":
        run()


if __name__ == "__main__":
    main()
