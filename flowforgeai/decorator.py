from loguru import logger
from typing import Dict, List, Callable


registered_functions: Dict = {}


def flowforge(func):
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling function {func.__name__}")
        return func(*args, **kwargs)

    registered_functions[func.__name__] = wrapper
    return wrapper


def get_registered_function(name: str) -> Callable:
    """Get a registered function by name."""
    if name not in registered_functions:
        raise ValueError(f"Function {name} not found in registered functions")
    return registered_functions[name]
