import pytest
from collections import defaultdict
from unittest.mock import MagicMock, patch

from promptmage import PromptMage, MageResult, Prompt
from promptmage.step import MageStep
from promptmage.mage import combine_dicts
from promptmage.storage import (
    PromptStore,
    DataStore,
)


@pytest.fixture
def mock_prompt_store():
    return MagicMock(spec=PromptStore)


@pytest.fixture
def mock_data_store():
    return MagicMock(spec=DataStore)


@pytest.fixture
def mock_step():
    step = MagicMock(spec=MageStep)
    step.name = "mock_step"
    step.execute.return_value = MageResult(
        id="result_1", results={"output": "result"}, next_step=None
    )
    step.initial = False
    step.signature = MagicMock()
    step.signature.parameters = {}
    return step


@pytest.fixture
def prompt_mage(mock_prompt_store, mock_data_store):
    return PromptMage(
        name="test_mage", prompt_store=mock_prompt_store, data_store=mock_data_store
    )


def test_initialization_with_provided_stores(mock_prompt_store, mock_data_store):
    pm = PromptMage(
        name="custom_test", prompt_store=mock_prompt_store, data_store=mock_data_store
    )
    assert pm.prompt_store == mock_prompt_store
    assert pm.data_store == mock_data_store


def test_step_decorator_registration(prompt_mage, mock_step):
    @prompt_mage.step(name="test_step")
    def mock_function():
        pass

    assert "test_step" in prompt_mage.steps
    assert isinstance(prompt_mage.steps["test_step"], MageStep)


def test_step_dependency_handling(prompt_mage):
    @prompt_mage.step(name="step1", depends_on="step0")
    def step1():
        pass

    @prompt_mage.step(name="step2", depends_on=["step0", "step1"])
    def step2():
        pass

    assert prompt_mage.dependencies["step1"] == ["step0"]
    assert prompt_mage.dependencies["step2"] == ["step0", "step1"]


def test_get_run_function(prompt_mage, mock_step):
    prompt_mage.steps[mock_step.name] = mock_step
    mock_step.initial = True

    run_function = prompt_mage.get_run_function()

    assert callable(run_function)


def test_run_function_execution(prompt_mage, mock_step):
    mock_step.initial = True
    prompt_mage.steps[mock_step.name] = mock_step

    run_function = prompt_mage.get_run_function()
    result = run_function()

    assert result == {"id": "result_1", "results": {"output": "result"}}
    assert mock_step.execute.called


def test_get_run_data(prompt_mage, mock_data_store):
    mock_data_store.get_all_data.return_value = [
        MagicMock(step_name="step1"),
        MagicMock(step_name="step2"),
    ]
    prompt_mage.steps["step1"] = MagicMock()
    prompt_mage.steps["step2"] = MagicMock()

    run_data = prompt_mage.get_run_data()

    assert len(run_data) == 2
    assert run_data[0].step_name == "step1"
    assert run_data[1].step_name == "step2"


def test_combine_dicts():
    list_of_dicts = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    combined = combine_dicts(list_of_dicts)
    assert combined == {"a": [1, 3], "b": 2, "c": 4}
