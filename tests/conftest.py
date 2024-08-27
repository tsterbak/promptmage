import os
import pytest
from typing import Generator

from promptmage.api import PromptMageAPI
from promptmage.frontend import PromptMageFrontend
from nicegui.testing import Screen, User

from promptmage.storage import SQLitePromptBackend, SQLiteDataBackend


pytest_plugins = ["nicegui.testing.plugin"]


@pytest.fixture
def user(user: User) -> Generator[User, None, None]:
    pm = PromptMageAPI(flows=[])
    app = pm.get_app()
    frontend = PromptMageFrontend(flows=pm.flows)
    frontend.init_from_api(app)
    yield user


@pytest.fixture
def screen(screen: Screen) -> Generator[Screen, None, None]:
    pm = PromptMageAPI(flows=[])
    app = pm.get_app()
    frontend = PromptMageFrontend(flows=pm.flows)
    frontend.init_from_api(app)
    yield screen


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
