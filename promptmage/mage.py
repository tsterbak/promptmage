from functools import partial
from typing import Dict
from loguru import logger
from functools import wraps


# Local imports
from .storage import StorageBackend


class PromptMage:
    def __init__(self, name: str, backend: StorageBackend | None = None):
        self.name: str = name
        self.backend = backend
        self.steps: Dict = {}
        logger.info(f"Initialized PromptMage with name: {name}")

    def step(self, name: str, prompt_id: str = None):
        """Decorator to add a step to the PromptMage instance.

        Args:
            name (str): The name of the step.
            prompt_id (str, optional): The ID of the prompt to use for this step. Defaults to None.
        """

        def decorator(func):
            # Get the prompt from the backend if it exists.
            if prompt_id and self.backend:
                prompt = self.backend.get_prompt(prompt_id)
            else:
                prompt = None

            # This is the actual decorator.
            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(f"Running step: {name}")
                logger.info(f"Step input: {args}, {kwargs}")
                # If the prompt exists, add it to the kwargs.
                if prompt:
                    kwargs["prompt"] = prompt

                output = func(*args, **kwargs)
                logger.info(f"Step output: {output}")
                return output

            self.steps[name] = wrapper  # partial(func, prompt=prompt)
            return wrapper

        return decorator

    def __repr__(self) -> str:
        return f"PromptMage(name={self.name}, steps={list(self.steps.keys())})"
