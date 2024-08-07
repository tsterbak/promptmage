import inspect
from loguru import logger
from functools import partial
from collections import defaultdict, deque
from typing import Dict, Callable, List


# Local imports
from .step import MageStep
from .result import MageResult
from .storage import PromptStore, DataStore, SQLitePromptBackend, SQLiteDataBackend


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
        available_models: List[str] | None = None,
    ):
        self.name: str = name
        self.prompt_store = (
            prompt_store if prompt_store else PromptStore(backend=SQLitePromptBackend())
        )
        self.data_store = (
            data_store if data_store else DataStore(backend=SQLiteDataBackend())
        )
        self.available_models = available_models
        self.steps: Dict[str, MageStep] = {}
        logger.info(f"Initialized PromptMage with name: {name}")

        # store the dependency graph
        self.dependencies = defaultdict(list)
        self.graph = defaultdict(list)
        self.indegree = defaultdict(int)

        # store the pass_through_inputs
        self.pass_through_inputs = {}

        # store execution results and details
        self.execution_results = []

    def step(
        self,
        name: str,
        prompt_name: str | None = None,
        depends_on: List[str] | str | None = None,
        initial: bool = False,
        one_to_many: bool = False,
        many_to_one: bool = False,
        pass_through_inputs: List[str] | None = None,
    ) -> Callable:
        """Decorator to add a step to the PromptMage instance.

        Args:
            name (str): The name of the step.
            prompt_name (str, optional): The name of the prompt to use for this step. Defaults to None.
            depends_on (str, optional): The name of the step that this step depends on. Defaults to None.
            initial (bool): Whether this step is an initial step. Defaults to False.
            one_to_many (bool, optional): Whether this step is a one-to-many step. Defaults to False.
            many_to_one (bool, optional): Whether this step is a many-to-one step. Defaults to False.
            pass_through_inputs (List[str], optional): The list of inputs to pass through to the step that requires them. Defaults to None.

        One-to-many steps are steps that are expected to return Iterable outputs. Following steps will be executed for each output.
        Many-to-one steps are steps that are expected to receive Iterable inputs. The step will be executed on all inputs together.
        """
        assert not (
            one_to_many and many_to_one
        ), "Cannot be both one-to-many and many-to-one."

        def decorator(func):
            # get the function signature
            func_params = inspect.signature(func).parameters

            # create and store the step
            self.steps[name] = MageStep(
                name=name,
                func=func,
                prompt_store=self.prompt_store,
                data_store=self.data_store,
                prompt_name=prompt_name,
                initial=initial,
                depends_on=depends_on,
                one_to_many=one_to_many,
                many_to_one=many_to_one,
                pass_through_inputs=pass_through_inputs,
                available_models=(
                    self.available_models if func_params.get("model") else None
                ),
                model=(
                    func_params.get("model").default
                    if func_params.get("model")
                    else None
                ),
            )

            # store the dependencies
            if depends_on:
                self.dependencies[name] = (
                    depends_on if isinstance(depends_on, list) else [depends_on]
                )
            else:
                self.dependencies[name] = []

            return func

        return decorator

    def _build_dependency_graph(self):
        """Builds the dependency graph of the PromptMage instance.

        Computes the indegree of each node in the graph.
        """
        self.graph.clear()
        self.indegree.clear()

        for func_id, deps in self.dependencies.items():
            for dep in deps:
                self.graph[dep].append(func_id)
                self.indegree[func_id] += 1
            if func_id not in self.indegree:
                self.indegree[func_id] = 0

    def _topological_sort(self) -> List:
        """Returns a topological sort of the dependency graph."""
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

    def get_run_function(self, start_from: str | None = None) -> Callable:
        initial_step_name = (
            [step.name for step in self.steps.values() if step.initial][0]
            if not start_from
            else start_from
        )
        first_func_node: MageStep = self.steps[initial_step_name]

        def run_function(**initial_inputs):
            """
            Execute steps starting from the initial step, following the next_step attribute.

            Args:
                **initial_inputs: The inputs for the initial step.
            """

            def execute_step(step_name: str, inputs: dict = None) -> MageResult:
                """
                Helper function to execute a step by its name.
                """
                logger.info(f"Executing step: {step_name}")
                step = self.steps[step_name]
                result = step.execute(**inputs)
                self.execution_results.append(
                    {
                        "step": step_name,
                        "result": result,
                        "step_id": step.step_id,
                        "next_step": (
                            result[-1].next_step
                            if isinstance(result, list)
                            else result.next_step
                        ),
                    }
                )

                if isinstance(result, list):
                    logger.info(f"Step: {step_name} returned multiple results.")
                    for res in result:
                        if res.next_step:
                            return execute_step(res.next_step, res.results)
                elif isinstance(result, MageResult) and result.next_step:
                    logger.info(f"Executing next step: {result.next_step}")
                    return execute_step(result.next_step, result.results)
                elif isinstance(result, MageResult) and not result.next_step:
                    logger.info("End of the path. Returning results.")
                    return result
                else:
                    logger.error(f"Invalid result type for step: {step_name}")

            # Start the execution from the initial step
            return execute_step(initial_step_name, initial_inputs).results

        # Set the signature of the returned function to match the first function in the graph
        run_function.__signature__ = first_func_node.signature
        return run_function

    def get_run_function_deprecated(self, start_from: str | None = None) -> Callable:
        """Returns a function that runs the PromptMage graph starting from the given step.

        Args:
            start_from (str, optional): The step to start the graph from. Defaults to None.
        """
        func_name = (
            [step.name for step in self.steps.values() if step.initial][0]
            if not start_from
            else start_from
        )
        first_func_node: MageStep = self.steps[func_name]

        def run_function(**initial_inputs):
            current_result = first_func_node.execute(**initial_inputs)
            if isinstance(current_result, list):
                pass
            while current_result.next_step:
                current_step = self.steps[current_result.next_step]
                current_result: MageResult = current_step.execute(
                    **current_result.results
                )
            return current_result.results

        # Set the signature of the returned function to match the first function in the graph
        run_function.__signature__ = first_func_node.signature

        return run_function

    def get_run_function_old(self, start_from=None) -> Callable:
        """Returns a function that runs the PromptMage graph starting from the given step.

        It has the same signature as the first function in the graph and takes these inputs.
        """
        self._build_dependency_graph()
        order = self._topological_sort()

        start_index = 0
        if start_from:
            start_index = order.index(start_from)

        def run_function(**initial_inputs):
            results = {}
            for step_id in order[start_index:]:
                step: MageStep = self.steps[step_id]
                # store the pass through inputs in self.pass_through_inputs
                if step.pass_through_inputs:
                    for pass_through_input in step.pass_through_inputs:
                        if pass_through_input in initial_inputs:
                            if pass_through_input not in self.pass_through_inputs:
                                self.pass_through_inputs[pass_through_input] = (
                                    initial_inputs[pass_through_input]
                                )
                            else:
                                logger.warning(
                                    f"Pass through input: {pass_through_input} already exists. Ignoring the new value."
                                )
                if step_id == order[start_index] and initial_inputs:
                    # If it's the first step and initial_inputs are provided, use them
                    results[step_id] = step.execute(**initial_inputs)
                else:
                    # Otherwise, get the inputs from the previous step
                    if self.dependencies[step_id]:
                        inputs = {
                            param: self.steps[dep].result
                            for dep, param in zip(
                                self.dependencies[step_id],
                                step.signature.parameters,
                            )
                        }
                    else:
                        inputs = {
                            param: step.input_values[param]
                            for param in step.signature.parameters
                        }
                    # inject the pass through inputs
                    for pass_through_input in self.pass_through_inputs:
                        if (
                            pass_through_input in step.signature.parameters
                            and pass_through_input not in inputs
                        ):
                            inputs[pass_through_input] = self.pass_through_inputs[
                                pass_through_input
                            ]
                    # execute the step
                    results[step_id] = step.execute(**inputs)
            # return the results of the last step
            return results[order[-1]]

        # Set the signature of the returned function to match the first function in the graph
        first_func_id = order[start_index]
        first_func_node: MageStep = self.steps[first_func_id]
        run_function.__signature__ = first_func_node.signature

        return run_function

    def __repr__(self) -> str:
        return f"PromptMage(name={self.name}, steps={list(self.steps.keys())})"

    def get_run_data(self) -> List:
        if self.data_store:
            runs = self.data_store.get_all_data()
            # filter by step_name
            return [run for run in runs if run.step_name in self.steps]
        return []
