from .mage import PromptMage
from .prompt import Prompt
from .run_data import RunData


import importlib.metadata

__version__ = importlib.metadata.version("promptmage")
title = """
╔═══╗                ╔╗ ╔═╗╔═╗             
║╔═╗║               ╔╝╚╗║║╚╝║║             
║╚═╝║╔═╗╔══╗╔╗╔╗╔══╗╚╗╔╝║╔╗╔╗║╔══╗ ╔══╗╔══╗
║╔══╝║╔╝║╔╗║║╚╝║║╔╗║ ║║ ║║║║║║╚ ╗║ ║╔╗║║╔╗║
║║   ║║ ║╚╝║║║║║║╚╝║ ║╚╗║║║║║║║╚╝╚╗║╚╝║║║═╣
╚╝   ╚╝ ╚══╝╚╩╩╝║╔═╝ ╚═╝╚╝╚╝╚╝╚═══╝╚═╗║╚══╝
                ║║                 ╔═╝║    
                ╚╝                 ╚══╝    
"""

__all__ = ["PromptMage", "Prompt", "RunData"]
