"""This module contains the Prompt class, which represents a prompt."""

from typing import Dict, List


class Prompt:
    """A class that represents a prompt.

    Attributes:
        prompt_id (str): The ID of the prompt.
        system (str): The system that generated the prompt.
        user (str): The user that the prompt is for.
        version (int): The version of the prompt.
        template_vars (List[str]): The template variables in the prompt.
    """

    def __init__(
        self,
        prompt_id: str,
        system: str,
        user: str,
        template_vars: List[str],
        version: int = 1,
    ):
        self.prompt_id = prompt_id
        self.system = system
        self.user = user
        self.version = version
        self.template_vars = template_vars

    def __repr__(self):
        return f"Prompt(id={self.prompt_id}, \
                version={self.version}, \
                system={self.system}, \
                user={self.user}), \
                template_vars={self.template_vars})"

    def to_dict(self):
        return {
            "prompt_id": self.prompt_id,
            "system": self.system,
            "user": self.user,
            "version": self.version,
            "template_vars": self.template_vars,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Prompt":
        return cls(
            prompt_id=data["prompt_id"],
            system=data["system"],
            user=data["user"],
            template_vars=data["template_vars"],
            version=data["version"],
        )
