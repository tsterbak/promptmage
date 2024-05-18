"""This module contains the PromptStore class, which implements the storage and retrieval of prompts with different backends."""

from typing import List

from promptmage.prompt import Prompt


class PromptStore:
    """A class that stores and retrieves prompts with different backends."""

    def __init__(self, backend):
        self.backend = backend

    def store_prompt(self, prompt: str):
        """Store a prompt in the backend."""
        self.backend.store_prompt(prompt.to_dict())

    def get_prompts(self) -> List[str]:
        """Retrieve all prompts from the backend."""
        return Prompt.from_dict(self.backend.get_prompts())
