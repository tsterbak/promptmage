import uuid
import inspect
from loguru import logger
from functools import wraps
from collections import defaultdict, deque
from typing import Dict, Callable, List


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

        self.dependencies = defaultdict(list)
        self.graph = defaultdict(list)
        self.indegree = defaultdict(int)

    def step(
        self, name: str, prompt_name: str, depends_on: List[str] | str | None = None
    ) -> Callable:
        """Decorator to add a step to the PromptMage instance.

        Args:
            name (str): The name of the step.
            prompt_name (str): The name of the prompt to use for this step. Defaults to None.
            depends_on (str, optional):
        """

        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(f"Running step: {name}...")
                logger.info(f"Step input: {args}, {kwargs}")
                # Get the prompt from the backend if it exists.
                prompt = self.prompt_store.get_prompt(prompt_name)
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
                        step_name=name,
                        prompt=prompt,
                        input_data={k: v for k, v in kwargs.items() if k != "prompt"},
                        output_data=results,
                    )
                    self.data_store.store_data(run_data)
                logger.info(f"Step output: {results}")
                return results

            self.steps[name] = MageStep(
                name=name,
                func=wrapper,
                prompt_store=self.prompt_store,
                prompt_name=prompt_name,
                depends_on=depends_on,
            )

            # store the dependencies
            if depends_on:
                self.dependencies[name] = (
                    depends_on if isinstance(depends_on, list) else [depends_on]
                )
            else:
                self.dependencies[name] = []

            return wrapper

        return decorator

    def _build_dependency_graph(self):
        # Build the graph and compute in-degrees of each node
        self.graph.clear()
        self.indegree.clear()

        for func_id, deps in self.dependencies.items():
            for dep in deps:
                self.graph[dep].append(func_id)
                self.indegree[func_id] += 1
            if func_id not in self.indegree:
                self.indegree[func_id] = 0

    def topological_sort(self):
        order = []
        queue = deque([node for node in self.indegree if self.indegree[node] == 0])

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in self.graph[node]:
                self.indegree[neighbor] -= 1
                if self.indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) == len(self.indegree):
            return order
        else:
            raise ValueError(
                "Cyclic dependency detected. This is currently not supported."
            )

    def get_run_function(self, start_from=None) -> Callable:
        """Returns a function that runs the PromptMage graph starting from the given step.

        It has the same signature as the first function in the graph and takes these inputs.
        """
        self._build_dependency_graph()
        order = self.topological_sort()

        start_index = 0
        if start_from:
            start_index = order.index(start_from)

        def run_function(**initial_inputs):
            results = {}
            for func_id in order[start_index:]:
                func_node: MageStep = self.steps[func_id]
                if func_id == order[start_index] and initial_inputs:
                    # If it's the first function and initial_inputs are provided, use them
                    results[func_id] = func_node.execute(**initial_inputs)
                else:
                    if self.dependencies[func_id]:
                        inputs = {
                            param: self.steps[dep].result
                            for dep, param in zip(
                                self.dependencies[func_id],
                                func_node.signature.parameters,
                            )
                        }
                    else:
                        inputs = {
                            param: func_node.input_values[param]
                            for param in func_node.signature.parameters
                        }
                    results[func_id] = func_node.execute(**inputs)
            # return the results of the last function
            return results[order[-1]]

        # Set the signature of the returned function to match the first function in the graph
        first_func_id = order[start_index]
        first_func_node: MageStep = self.steps[first_func_id]
        run_function.__signature__ = first_func_node.signature

        return run_function

    def __repr__(self) -> str:
        return f"PromptMage(name={self.name}, steps={list(self.steps.keys())})"


class MageStep:
    def __init__(
        self,
        name: str,
        func: Callable,
        prompt_store: PromptStore,
        prompt_name: str | None = None,
        depends_on: str | None = None,
    ):
        self.step_id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.signature = inspect.signature(func)
        self.prompt_store = prompt_store
        self.prompt_name = prompt_name
        self.depends_on = depends_on

        # store inputs and results
        self.input_values = {}
        self.result = None

        # Initialize input values with default parameter values
        for param in self.signature.parameters.values():
            if param.name == "prompt":
                continue
            if param.default is not inspect.Parameter.empty:
                self.input_values[param.name] = param.default
            else:
                self.input_values[param.name] = None

        # callbacks for the frontend
        self._input_callbacks = []
        self._output_callbacks = []

    def execute(self, **inputs):
        for key, value in inputs.items():
            self.input_values[key] = value
        for callback in self._input_callbacks:
            callback()
        self.result = self.func(**self.input_values)
        # run the callbacks
        for callback in self._output_callbacks:
            callback()
        return self.result

    def __repr__(self):
        return f"Step(step_id={self.step_id}, name={self.name}, prompt_name={self.prompt_name}, depends_on={self.depends_on})"

    def get_prompt(self) -> Prompt:
        return self.prompt_store.get_prompt(self.prompt_name)

    def set_prompt(self, prompt: Prompt):
        self.prompt_store.store_prompt(prompt)

    def on_input_change(self, callback):
        self._input_callbacks.append(callback)

    def on_output_change(self, callback):
        self._output_callbacks.append(callback)
