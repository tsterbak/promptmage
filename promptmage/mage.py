import inspect
from loguru import logger
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

        # store the running status
        self.is_running = False

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
                initial_inputs (dict): The inputs for the initial step.
            """
            self.is_running = True
            self.execution_results = []

            def execute_graph(
                step_name: str,
                inputs: dict | None = None,
                previous_result_ids: List | None = None,
            ) -> MageResult:
                """
                Helper function to execute a step by its name.
                """
                logger.info(f"Executing step: {step_name}")
                current_node = step_name
                current_data = inputs

                while current_node:
                    logger.warning(f"Current node: {current_node}")
                    # Get the current step
                    step = self.steps[current_node]

                    # Execute the step
                    if isinstance(current_data, list):
                        current_data = combine_dicts(current_data)
                    # check if all required inputs are available else return
                    if not all(
                        input_param in current_data.keys()
                        for input_param in step.signature.parameters
                        if input_param not in ["prompt", "model"]
                    ):
                        logger.warning(
                            f"Step {current_node} requires additional inputs. Returning."
                        )
                        break
                    response = step.execute(**current_data)

                    # Store current and previous result ids
                    if previous_result_ids is None:
                        previous_result_ids = []
                    if isinstance(response, list):
                        for res in response:
                            self.execution_results.append(
                                {
                                    "previous_result_ids": previous_result_ids,
                                    "current_result_id": res.id,
                                    "step": step.name,
                                    "results": res.results,
                                }
                            )
                        previous_result_ids = [res.id for res in response]
                    else:
                        self.execution_results.append(
                            {
                                "previous_result_ids": previous_result_ids,
                                "current_result_id": response.id,
                                "step": step.name,
                                "results": response.results,
                            }
                        )
                        previous_result_ids = [response.id]

                    # Store the execution results
                    if isinstance(response, list):
                        result = response
                        next_node = [r.next_step for r in response]
                    elif isinstance(response, MageResult):
                        next_node = response.next_step
                        result = response
                    else:
                        raise ValueError(
                            f"Step {current_node} returned an invalid response type."
                        )
                    if isinstance(next_node, list):  # Multiple next nodes
                        if isinstance(result, list):
                            logger.warning("Multiple next nodes and multiple results.")
                            # Map the next_node to each result item
                            current_node = next_node
                            current_data = []
                            next_node = None
                            previous_result_ids_list = []
                            for r, n in zip(result, current_node):
                                d, next_node, previous_result_idx = execute_graph(
                                    step_name=n,
                                    inputs=r.results,
                                    previous_result_ids=[r.id],
                                )
                                current_data.append(d)
                                previous_result_ids_list.append(previous_result_idx)
                            previous_result_ids = [
                                id for ids in previous_result_ids_list for id in ids
                            ]
                            current_node = next_node
                        else:
                            logger.warning("Multiple next nodes and single result.")
                            # Passing the single result to each next node
                            current_data = []
                            current_node = next_node
                            next_nodes = []
                            previous_result_ids = []
                            for n in current_node:
                                res, next_node, pid = execute_graph(
                                    step_name=n,
                                    inputs=result.results,
                                    previous_result_ids=[result.id],
                                )
                                previous_result_ids.extend(pid)
                                current_data.append(res)
                                next_nodes.append(next_node)
                            # if all the next node are the same, then we can just use the first one else raise an error
                            if len(set(next_nodes)) == 1:
                                current_node = next_nodes[0]
                            else:
                                raise ValueError(
                                    "Multiple next nodes and single result. Next nodes are different."
                                )
                    else:
                        if isinstance(result, list):
                            logger.warning("Single next node and multiple results.")
                            current_node = next_node
                            current_data = []
                            next_node = None
                            for r in result:
                                d, next_node, previous_result_ids = execute_graph(
                                    step_name=current_node,
                                    inputs=r.results,
                                    previous_result_ids=[r.id],
                                )
                                current_data.append(d)
                            current_node = next_node
                        else:
                            if next_node and self.steps[next_node].many_to_one:
                                logger.warning(
                                    "Single next node and many-to-one result."
                                )
                                current_data = result.results
                                current_node = next_node
                                break
                            else:
                                logger.warning("Single next node and single result.")
                                current_node = next_node
                                current_data = result.results

                return (
                    current_data,
                    current_node,
                    previous_result_ids if previous_result_ids else None,
                )

            final_result, _, _ = execute_graph(initial_step_name, initial_inputs)
            self.is_running = False
            return final_result

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


def combine_dicts(list_of_dicts):
    # Initialize a defaultdict where each key will hold a list of values
    combined_dict = defaultdict(list)

    # Iterate through each dictionary in the list
    for d in list_of_dicts:
        for key, value in d.items():
            combined_dict[key].append(value)

    # Convert lists with a single value back to that value
    final_dict = {
        key: (value[0] if len(value) == 1 else value)
        for key, value in combined_dict.items()
    }

    return final_dict
