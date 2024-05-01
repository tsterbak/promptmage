"""This module contains the command line interface for the flowforge package."""

import uvicorn
from importlib import import_module
from pathlib import Path
import sys


def serve(file_path: str):
    # Dynamically import the application module
    sys.path.append(
        str(Path(file_path).parent.absolute())
    )  # Add the directory of the file to PYTHONPATH
    module_name = Path(file_path).stem
    spec = import_module(module_name)

    # Assuming there is a FlowForge instance named `flow` in the module
    flow = getattr(spec, "flow")
    app = flow.serve()

    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    serve(sys.argv[1])
