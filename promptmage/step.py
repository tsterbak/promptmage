import uuid
import inspect
from typing import Callable, List
from loguru import logger

from .prompt import Prompt
from .run_data import RunData
from .result import MageResult
from .storage import PromptStore, DataStore


class MageStep:
    """A class to represent a step in a PromptMage instance.

    Attributes:
        step_id (str): The unique identifier for the step.
        name (str): The name of the step.
        func (Callable): The function to execute for the step.
        signature (inspect.Signature): The signature of the function.
        prompt_store (PromptStore): The prompt store to use for storing prompts.
        data_store (DataStore): The data store to use for storing data.
        prompt_name (str): The name of the prompt associated with the step.
        depends_on (str): The name of the step that this step depends on.
        initial (bool): Whether the step is an initial step.
        one_to_many (bool): Whether the step is a one-to-many step.
        many_to_one (bool): Whether the step is a many-to-one step.
        model (str): The model to use for the step.
        available_models (List[str]): The available models for the step.
        pass_through_inputs (List[str]): The inputs to pass through to the next step.
    """

    def __init__(
        self,
        name: str,
        func: Callable,
        prompt_store: PromptStore,
        data_store: DataStore,
        prompt_name: str | None = None,
        depends_on: str | None = None,
        initial: bool = False,
        one_to_many: bool = False,
        many_to_one: bool = False,
        model: str | None = None,
        available_models: List[str] | None = None,
        pass_through_inputs: List[str] | None = None,
    ):
        self.step_id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.signature = inspect.signature(func)
        self.prompt_store = prompt_store
        self.data_store = data_store
        self.prompt_name = prompt_name
        self.depends_on = depends_on
        self.initial = initial
        self.one_to_many = one_to_many
        self.many_to_one = many_to_one
        self.model = model
        self.available_models = available_models
        self.pass_through_inputs = pass_through_inputs

        # store inputs and results
        self.input_values = {}
        self.result = None

        # Initialize input values with default parameter values
        for param in self.signature.parameters.values():
            if param.name in ["prompt", "model"]:
                continue
            if param.default is not inspect.Parameter.empty:
                self.input_values[param.name] = param.default
            else:
                self.input_values[param.name] = None

        # callbacks for the frontend
        self._input_callbacks = []
        self._output_callbacks = []

    def execute(self, **inputs):
        """Execute the step with the given inputs."""
        logger.info(f"Executing step: {self.name}...")
        multi_input_param = None
        # set the inputs
        logger.info(f"Setting inputs: {inputs.keys()}")
        for key, value in inputs.items():
            if isinstance(value, list):
                multi_input_param = key
            self.input_values[key] = value
        # set the model
        if self.model:
            self.input_values["model"] = self.model
        # get the prompt and set it if exists
        if self.prompt_name:
            prompt = self.get_prompt()
            self.input_values["prompt"] = prompt
        else:
            prompt = None
        # run the input callbacks
        for callback in self._input_callbacks:
            callback()
        # execute the function and store the result
        try:
            if self.one_to_many:
                logger.info("Executing step one-to-many")
                self.result = []
                if multi_input_param:
                    param_values = self.input_values[multi_input_param]
                    for value in param_values:
                        self.input_values[multi_input_param] = value
                        self.result.append(self.func(**self.input_values))
                    self.input_values[multi_input_param] = param_values
                else:
                    raise ValueError(
                        "One-to-many step requires a list input parameter."
                    )
            elif self.many_to_one:
                logger.info("Executing step many-to-one")
                self.result = self.func(**self.input_values)
            else:
                logger.info("Executing step normally")
                self.result = self.func(**self.input_values)
            status = "success"
        except Exception as e:
            self.result = MageResult(error=f"Error: {e}")
            status = "failed"
        # store the run data
        self.store_run(prompt=prompt, status=status)
        # run the output callbacks
        for callback in self._output_callbacks:
            callback()
        logger.info(f"Step {self.name} executed successfully.")
        return self.result

    def __repr__(self):
        return f"Step(step_id={self.step_id}, name={self.name}, prompt_name={self.prompt_name}, depends_on={self.depends_on})"

    def get_prompt(self) -> Prompt:
        return self.prompt_store.get_prompt(self.prompt_name)

    def set_prompt(self, prompt: Prompt):
        prompt.id = str(uuid.uuid4())
        prompt.version = prompt.version + 1
        self.prompt_store.store_prompt(prompt)

    def store_run(
        self,
        prompt: Prompt | None = None,
        status: str = "success",
    ):
        """Store the run data in the data store."""
        if self.data_store:
            run_data = RunData(
                step_name=self.name,
                prompt=prompt if self.prompt_name else None,
                input_data={
                    k: v
                    for k, v in self.input_values.items()
                    if k not in ["prompt", "model"]
                },
                output_data=(
                    [r.results for r in self.result]
                    if isinstance(self.result, list)
                    else self.result.results
                ),
                status=status,
                model=self.model,
            )
            self.data_store.store_data(run_data)

    def on_input_change(self, callback):
        self._input_callbacks.append(callback)

    def on_output_change(self, callback):
        self._output_callbacks.append(callback)
