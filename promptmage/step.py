import uuid
import inspect
from typing import Callable, List
from loguru import logger

from .prompt import Prompt
from .run_data import RunData
from .storage import PromptStore, DataStore


class MageStep:
    def __init__(
        self,
        name: str,
        func: Callable,
        prompt_store: PromptStore,
        data_store: DataStore,
        prompt_name: str | None = None,
        depends_on: str | None = None,
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
        # set the inputs
        logger.info(f"Setting inputs: {inputs.keys()}")
        for key, value in inputs.items():
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
            self.result = self.func(**self.input_values)
            status = "success"
        except Exception as e:
            self.result = f"Error: {e}"
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
                output_data=self.result,
                status=status,
                model=self.model,
            )
            self.data_store.store_data(run_data)

    def on_input_change(self, callback):
        self._input_callbacks.append(callback)

    def on_output_change(self, callback):
        self._output_callbacks.append(callback)