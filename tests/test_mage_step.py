import pytest

from promptmage.mage import MageStep


def test_init_mage_step():
    step = MageStep(
        name="test_step", func=lambda x: x, prompt_store=None, data_store=None
    )
    assert step.name == "test_step"
    assert step.func(5) == 5
    assert step.prompt_store is None

    assert step.input_values == {"x": None}
    assert step.result is None


def test_execute_mage_step():
    step = MageStep(
        name="test_step", func=lambda x: x + 1, prompt_store=None, data_store=None
    )
    step.execute(x=5)
    assert step.result == 6
    assert step.input_values == {"x": 5}
