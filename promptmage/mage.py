import uuid
import inspect
from loguru import logger
from functools import wraps
from typing import Dict, Callable


# Local imports
from .prompt import Prompt
from .run_data import RunData
from .storage import PromptStore, DataStore


class PromptMage:
    """A class to represent a PromptMage instance.

    Attributes:
        name (str): The name of the PromptMage instance.
        prompt_store (PromptStore): The prompt store to use for storing prompts.
        data_store (DataStore): The data store to use for storing data.
        steps (Dict): A dictionary of steps in the PromptMage instance.
    """

    def __init__(
        self,
        name: str,
        prompt_store: PromptStore | None = None,
        data_store: DataStore | None = None,
    ):
        self.name: str = name
        self.prompt_store = prompt_store
        self.data_store = data_store
        self.steps: Dict = {}
        logger.info(f"Initialized PromptMage with name: {name}")

    def step(self, name: str, prompt_id: str, depends_on: str = None) -> Callable:
        """Decorator to add a step to the PromptMage instance.

        Args:
            name (str): The name of the step.
            prompt_id (str): The ID of the prompt to use for this step. Defaults to None.
            depends_on (str, optional):
        """

        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(f"Running step: {self.name}...")
                logger.info(f"Step input: {args}, {kwargs}")
                # Get the prompt from the backend if it exists.
                prompt = self.prompt_store.get_prompt(prompt_id)
                # extract the template variables from the function signature
                if prompt.template_vars == []:
                    sig = inspect.signature(func)
                    prompt.template_vars = [
                        param for param in sig.parameters if param != "prompt"
                    ]
                    # Store the updated prompt
                    self.prompt_store.store_prompt(prompt)
                # Add the prompt to the kwargs
                kwargs["prompt"] = prompt
                try:
                    results = func(*args, **kwargs)
                except KeyError as e:
                    results = f"Error: {e}"

                # Store input and output data
                if self.data_store:
                    run_data = RunData(
                        run_id=uuid.uuid4(),
                        prompt=prompt,
                        input_data=args,
                        output_data=results,
                    )
                    self.data_store.store_data(run_data)
                logger.info(f"Step output: {results}")
                return results

            self.steps[name] = MageStep(
                name=name,
                func=wrapper,
                prompt_store=self.prompt_store,
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
        prompt_store: PromptStore,
        prompt_id: str | None = None,
        depends_on: str | None = None,
    ):
        self.step_id = uuid.uuid4()
        self.name = name
        self.func = func
        self.prompt_store = prompt_store
        self.prompt_id = prompt_id
        self.depends_on = depends_on

    def __repr__(self):
        return f"Step(prompt_id={self.prompt_id}, name={self.name}, prompt_id={self.prompt_id}, depends_on={self.depends_on})"

    def get_prompt(self) -> Prompt:
        return self.prompt_store.get_prompt(self.prompt_id)
