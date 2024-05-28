"""This module contains the RunData class, which is used to represent the data for a single run of a promptmage flow."""

import uuid
from datetime import datetime
from typing import Dict

from promptmage.prompt import Prompt


class RunData:
    """A class that represents the data for a single run of a promptmage flow."""

    def __init__(
        self,
        step_name: str,
        prompt: Prompt,
        input_data: Dict,
        output_data: Dict,
        run_id: str | None = None,
        run_time: datetime = datetime.now(),
    ):
        self.run_id = run_id if run_id else str(uuid.uuid4())
        self.step_name = step_name
        self.run_time = run_time
        self.prompt = prompt
        self.input_data = input_data
        self.output_data = output_data

    def __repr__(self) -> str:
        return (
            f"RunData(run_id={self.run_id}, "
            f"step_name={self.step_name}, "
            f"run_time={self.run_time}, "
            f"prompt={self.prompt}, "
            f"input_data={self.input_data}, "
            f"output_data={self.output_data})"
        )

    def to_dict(self) -> Dict:
        return {
            "prompt": self.prompt.to_dict(),
            "step_name": self.step_name,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "run_id": self.run_id,
            "run_time": self.run_time,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["step_name"],
            data["prompt"],
            data["input_data"],
            data["output_data"],
            data["run_id"],
            data["run_time"],
        )
