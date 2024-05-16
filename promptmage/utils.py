import sys
from pathlib import Path
from importlib import import_module

from promptmage import PromptMage


def get_flow(file_path: str):
    sys.path.append(
        str(Path(file_path).parent.absolute())
    )  # Add the directory of the file to PYTHONPATH
    module_name = Path(file_path).stem
    module = import_module(module_name)

    # Find an instance of FlowForge in the module
    flow_instance = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, PromptMage):
            flow_instance = attr
            break
    return flow_instance
