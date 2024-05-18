"""This module contains the Prompt class, which represents a prompt."""


class Prompt:
    def __init__(self, prompt_id: str, system_prompt: str, user_prompt: str):
        self.prompt_id = prompt_id
        self.system = system_prompt
        self.user = user_prompt

    def __repr__(self):
        return f"<Prompt id={self.prompt_id}>, system={self.system}, user={self.user}>"

    def to_dict(self):
        return {"prompt_id": self.prompt_id, "system": self.system, "user": self.user}

    @classmethod
    def from_dict(cls, data):
        return cls(data["prompt_id"])
