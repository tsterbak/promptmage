"""This module contains the Prompt class, which represents a prompt."""

import uuid
from typing import Dict, List


class Prompt:
    """A class that represents a prompt.

    Attributes:
        name (str): The name of the prompt.
        prompt_id (str): The ID of the prompt.
        system (str): The system that generated the prompt.
        user (str): The user that the prompt is for.
        version (int): The version of the prompt.
        template_vars (List[str]): The template variables in the prompt.
        id (str): The unique identifier for the prompt.
        active (bool): Whether the prompt is active.
    """

    def __init__(
        self,
        name: str,
        system: str,
        user: str,
        template_vars: List[str],
        version: int = 1,
        id: str | None = None,
        active: bool = False,
    ):
        self.name = name
        self.id = id if id else str(uuid.uuid4())
        self.system = system
        self.user = user
        self.version = version
        self.template_vars = template_vars
        self.active = active

    def __repr__(self):
        return f"Prompt(id={self.id}, \
                name={self.name}, \
                version={self.version}, \
                active={self.active}, \
                system={self.system}, \
                user={self.user}), \
                template_vars={self.template_vars})"

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "active": self.active,
            "system": self.system,
            "user": self.user,
            "version": self.version,
            "template_vars": self.template_vars,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Prompt":
        return cls(
            name=data["name"],
            id=data["id"],
            active=data["active"],
            system=data["system"],
            user=data["user"],
            template_vars=data["template_vars"],
            version=data["version"],
        )
