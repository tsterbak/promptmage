from functools import partial
from typing import Dict


# Local imports
from .storage import StorageBackend


class PromptMage:
    def __init__(self, name: str, backend: StorageBackend | None = None):
        self.name: str = name
        self.backend = backend
        self.steps: Dict = {}
        print(f"Initialized PromptMage with name: {name}")

    def step(self, name: str, prompt_id: str = None):
        """Decorator to add a step to the PromptMage instance.

        Args:
            name (str): The name of the step.
            prompt_id (str, optional): The ID of the prompt to use for this step. Defaults to None.
        """
        # Load the prompt if provided

        def decorator(func):
            if prompt_id and self.backend:
                prompt = self.backend.get_prompt(prompt_id)
            else:
                prompt = None

            # This is the actual decorator.
            def wrapper(*args, **kwargs):
                if prompt:
                    kwargs["prompt"] = prompt
                    return func(*args, **kwargs)
                return func(*args, **kwargs)

            self.steps[name] = partial(func, prompt=prompt)
            return wrapper

        return decorator

    def __repr__(self) -> str:
        return f"PromptMage(name={self.name}, steps={list(self.steps.keys())})"

    def get_frontend(self):
        pass
