import inspect
import types
from typing import Dict, Callable
from loguru import logger
from functools import wraps
import uuid


# Local imports
from .storage import StorageBackend


class PromptMage:
    def __init__(self, name: str, backend: StorageBackend | None = None):
        self.name: str = name
        self.backend = backend
        self.steps: Dict = {}
        logger.info(f"Initialized PromptMage with name: {name}")

    def step(self, name: str, prompt_id: str = None, depends_on: str = None):
        """Decorator to add a step to the PromptMage instance.

        Args:
            name (str): The name of the step.
            prompt_id (str, optional): The ID of the prompt to use for this step. Defaults to None.
            depends_on (str, optional):
        """

        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(f"Running step: {self.name}...")
                logger.info(f"Step input: {args}, {kwargs}")
                # TODO: store input in the backend
                # Get the prompt from the backend if it exists.
                if prompt_id and self.backend:
                    prompt = self.backend.get_prompt(prompt_id)
                else:
                    prompt = None
                # If the prompt exists, add it to the kwargs.
                if prompt:
                    kwargs["prompt"] = prompt
                results = func(*args, **kwargs)
                # TODO: store output in the backend
                logger.info(f"Step output: {results}")
                return results

            self.steps[name] = MageStep(
                name=name,
                func=wrapper,
                backend=self.backend,
                prompt_id=prompt_id,
                depends_on=depends_on,
            )

            return wrapper

        return decorator

    def __repr__(self) -> str:
        return f"PromptMage(name={self.name}, steps={list(self.steps.keys())})"


class MageStep:
    def __init__(
        self,
        name: str,
        func: Callable,
        backend: StorageBackend,
        prompt_id: str | None = None,
        depends_on: str | None = None,
    ):
        self.step_id = uuid.uuid4()
        self.name = name
        self.func = func
        self.backend = backend
        self.prompt_id = prompt_id
        self.depends_on = depends_on

    def __repr__(self):
        return f"Step(prompt_id={self.prompt_id}, name={self.name}, prompt_id={self.prompt_id}, depends_on={self.depends_on})"
