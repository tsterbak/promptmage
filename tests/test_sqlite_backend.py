"""Tests for the sqlite backends for prompts and run data."""

import pytest
import sqlite3

from promptmage.storage import SQLitePromptBackend, SQLiteDataBackend
from promptmage import Prompt, RunData


def test_init_backend():
    """Test that the database is initialized correctly."""
    db_path = ":memory:"
    # Create a prompt backend
    prompt_backend = SQLitePromptBackend(db_path)
    assert prompt_backend.db_path == db_path


def test_store_prompt(prompt_sqlite_backend):
    """Test that a prompt is stored correctly."""
    prompt = Prompt(
        name="test",
        system="test",
        user="test",
        version=1,
        template_vars=["test"],
        active=False,
    )

    prompt_sqlite_backend.store_prompt(prompt)

    # Check that the prompt is stored correctly
    conn = sqlite3.connect(prompt_sqlite_backend.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prompts WHERE id=?", (prompt.id,))
    row = cursor.fetchone()
    assert row == (
        prompt.id,
        prompt.name,
        prompt.system,
        prompt.user,
        prompt.version,
        ",".join(prompt.template_vars),
        prompt.active,
    )


def test_get_prompt(prompt_sqlite_backend):
    """Test that a prompt is retrieved correctly."""
    prompt = Prompt(
        name="test",
        system="test",
        user="test",
        version=1,
        template_vars=["test"],
    )
    prompt_sqlite_backend.store_prompt(prompt)

    # Check that the prompt is retrieved correctly
    retrieved_prompt = prompt_sqlite_backend.get_prompt(prompt.name)
    assert retrieved_prompt.id == prompt.id
    assert retrieved_prompt.name == prompt.name
    assert retrieved_prompt.system == prompt.system
    assert retrieved_prompt.user == prompt.user
    assert retrieved_prompt.version == prompt.version
    assert retrieved_prompt.template_vars == prompt.template_vars


def test_get_prompts(prompt_sqlite_backend):
    """Test that all prompts are retrieved correctly."""
    prompt1 = Prompt(
        name="test1",
        system="test1",
        user="test1",
        version=1,
        template_vars=["test1"],
    )
    prompt2 = Prompt(
        name="test2",
        system="test2",
        user="test2",
        version=2,
        template_vars=["test2"],
    )
    prompt_sqlite_backend.store_prompt(prompt1)
    prompt_sqlite_backend.store_prompt(prompt2)

    # Check that the prompts are retrieved correctly
    prompts = prompt_sqlite_backend.get_prompts()
    assert len(prompts) == 2
    assert prompts[0].id == prompt1.id
    assert prompts[0].name == prompt1.name
    assert prompts[0].system == prompt1.system
    assert prompts[0].user == prompt1.user
    assert prompts[0].version == prompt1.version
    assert prompts[0].template_vars == prompt1.template_vars
    assert prompts[1].id == prompt2.id
    assert prompts[1].name == prompt2.name
    assert prompts[1].system == prompt2.system
    assert prompts[1].user == prompt2.user
    assert prompts[1].version == prompt2.version
    assert prompts[1].template_vars == prompt2.template_vars


def test_store_run_data(data_sqlite_backend):
    """Test that run data is stored correctly."""
    run_data = RunData(
        run_id="test",
        prompt=Prompt(
            name="test",
            system="test",
            user="test",
            version=1,
            template_vars=["test"],
        ),
        step_name="test",
        input_data={"test": "test"},
        output_data={"test": "test"},
        status="test",
        model="test",
        execution_time=1.0,
        run_time="test",
    )

    data_sqlite_backend.store_data(run_data)

    # Check that the run data is stored correctly
    conn = sqlite3.connect(data_sqlite_backend.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data WHERE run_id=?", (run_data.run_id,))
    row = cursor.fetchone()

    assert row[0] == run_data.step_run_id
    assert row[1] == run_data.run_time
    assert row[2] == run_data.execution_time


def test_get_run_data(data_sqlite_backend):
    """Test that run data is retrieved correctly."""


def test_get_run_data_by_prompt(data_sqlite_backend):
    """Test that run data is retrieved correctly by prompt."""
