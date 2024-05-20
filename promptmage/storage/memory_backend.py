"""This module contains the InMemoryBackend class, which implements a simple in-memory storage backend for prompts."""

from typing import Dict

from promptmage.prompt import Prompt
from promptmage.storage import StorageBackend


class InMemoryBackend(StorageBackend):
    """A simple in-memory storage backend for prompts."""

    def __init__(self, prompts: Dict[str, Prompt]):
        self.prompts = prompts

    def store_prompt(self, prompt: Dict):
        """Store a prompt in memory."""
        self.prompts[prompt["id"]] = prompt["text"]

    def get_prompt(self, prompt_id: str) -> str:
        """Retrieve a prompt from memory."""
        return self.prompts.get(prompt_id)

    def get_prompts(self) -> Dict:
        """Retrieve all prompts from memory."""
        return self.prompts
