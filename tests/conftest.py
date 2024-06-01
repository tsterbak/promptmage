import os
import pytest

from promptmage.storage import SQLitePromptBackend, SQLiteDataBackend


@pytest.fixture
def db_path():
    return "tests/tmp/test_promptmage.db"


@pytest.fixture
def prompt_sqlite_backend(db_path):
    yield SQLitePromptBackend(db_path)

    # Clean up the database
    os.remove(db_path)


@pytest.fixture
def data_sqlite_backend(db_path):
    yield SQLiteDataBackend(db_path)

    # Clean up the database
    os.remove(db_path)
