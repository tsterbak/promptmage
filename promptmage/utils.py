import sys
from pathlib import Path
from typing import List
from importlib import import_module

from promptmage import PromptMage


def get_flows(file_path: str) -> List[PromptMage]:
    sys.path.append(
        str(Path(file_path).parent.absolute())
    )  # Add the directory of the file to PYTHONPATH
    module_name = Path(file_path).stem
    module = import_module(module_name)

    # Find an instances of PromptMage in the module
    flows = []
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, PromptMage):
            flows.append(attr)
    return flows
