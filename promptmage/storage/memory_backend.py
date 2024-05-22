"""This module contains the InMemoryBackend class, which implements a simple in-memory storage backend for prompts."""

from typing import Dict

from promptmage.prompt import Prompt
from promptmage.run_data import RunData
from promptmage.storage import StorageBackend


class InMemoryPromptBackend(StorageBackend):
    """A simple in-memory storage backend for prompts."""

    def __init__(self):
        self.prompts: Dict[str, Prompt] = {}

    def store_prompt(self, prompt: Prompt):
        """Store a prompt in memory."""
        self.prompts[prompt.prompt_id] = prompt.to_dict()

    def get_prompt(self, prompt_id: str) -> str:
        """Retrieve a prompt from memory."""
        return Prompt.from_dict(self.prompts.get(prompt_id))

    def get_prompts(self) -> Dict:
        """Retrieve all prompts from memory."""
        return self.prompts


class InMemoryDataBackend(StorageBackend):
    """A simple in-memory storage backend for data."""

    def __init__(self):
        self.data: Dict[str, RunData] = {}

    def store_data(self, run: RunData):
        """Store data in memory."""
        self.data[run.run_id] = run.to_dict()

    def get_data(self, run_id: str) -> str:
        """Retrieve data from memory."""
        return RunData.from_dict(self.data.get(run_id))

    def get_all_data(self) -> Dict:
        """Retrieve all data from memory."""
        return self.data
