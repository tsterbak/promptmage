"""This module contains the Prompt class, which represents a prompt."""

from typing import Dict


class Prompt:
    """A class that represents a prompt.

    Attributes:
        prompt_id (str): The ID of the prompt.
        system (str): The system that generated the prompt.
        user (str): The user that the prompt is for.
        version (int): The version of the prompt.
    """

    def __init__(self, prompt_id: str, system: str, user: str, version: int = 1):
        self.prompt_id = prompt_id
        self.system = system
        self.user = user
        self.version = version

    def __repr__(self):
        return f"Prompt(id={self.prompt_id}, \
                version={self.version}, \
                system={self.system}, \
                user={self.user})"

    def to_dict(self):
        return {
            "prompt_id": self.prompt_id,
            "system": self.system,
            "user": self.user,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Prompt":
        return cls(
            prompt_id=data["prompt_id"],
            system=data["system"],
            user=data["user"],
            version=data["version"],
        )
