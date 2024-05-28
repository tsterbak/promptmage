"""This module contains the InMemoryBackend class, which implements a simple in-memory storage backend for prompts."""

from typing import Dict

from promptmage.prompt import Prompt
from promptmage.run_data import RunData
from promptmage.storage import StorageBackend
from promptmage.exceptions import PromptNotFoundException


class InMemoryPromptBackend(StorageBackend):
    """A simple in-memory storage backend for prompts."""

    def __init__(self):
        self.prompts: Dict[str, Prompt] = {}

    def store_prompt(self, prompt: Prompt):
        """Store a prompt in memory."""
        self.prompts[prompt.name] = prompt.to_dict()

    def get_prompt(self, prompt_name: str) -> str:
        """Retrieve a prompt from memory."""
        if prompt_name not in self.prompts:
            raise PromptNotFoundException(f"Prompt with name {prompt_name} not found.")
        return Prompt.from_dict(self.prompts.get(prompt_name))

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
