"""This module contains the RunData class, which is used to represent the data for a single run of a promptmage flow."""

import uuid
from datetime import datetime
from typing import Dict

from promptmage.prompt import Prompt


class RunData:
    """A class that represents the data for a single run of a promptmage flow."""

    def __init__(
        self,
        prompt: Prompt,
        input_data: Dict,
        output_data: Dict,
        run_id: str = str(uuid.uuid4()),
        run_time: datetime = datetime.now(),
    ):
        self.run_id = run_id
        self.run_time = run_time
        self.prompt = prompt
        self.input_data = input_data
        self.output_data = output_data

    def __repr__(self) -> str:
        return f"RunData(run_id={self.run_id}, run_time={self.run_time}, prompt={self.prompt}, input_data={self.input_data}, output_data={self.output_data})"

    def to_dict(self) -> Dict:
        return {
            "prompt": self.prompt.to_dict(),
            "input_data": self.input_data,
            "output_data": self.output_data,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["prompt"],
            data["input_data"],
            data["output_data"],
            data["run_id"],
            data["run_time"],
        )
