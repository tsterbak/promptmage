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
        run_id: str = str(uuid.uuid4()),
        step_run_id: str | None = None,
        run_time: datetime | None = None,
        execution_time: float | None = None,  # execution_time in seconds
        status: str | None = None,
        model: str | None = None,
    ):
        self.step_run_id = step_run_id if step_run_id else str(uuid.uuid4())
        self.run_id = run_id
        self.step_name = step_name
        self.run_time = run_time if run_time else str(datetime.now())
        self.execution_time = execution_time
        self.prompt = prompt
        self.input_data = input_data
        self.output_data = output_data
        self.status = status
        self.model = model

    def __repr__(self) -> str:
        return (
            f"RunData(run_id={self.run_id}, "
            f"step_run_id={self.step_run_id}, "
            f"step_name={self.step_name}, "
            f"status={self.status}, "
            f"run_time={self.run_time}, "
            f"execution_time={self.execution_time}, "
            f"prompt={self.prompt}, "
            f"input_data={self.input_data}, "
            f"output_data={self.output_data}, "
            f"model={self.model})"
        )

    def to_dict(self) -> Dict:
        return {
            "prompt": self.prompt.to_dict() if self.prompt else None,
            "step_name": self.step_name,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "run_id": self.run_id,
            "step_run_id": self.step_run_id,
            "run_time": self.run_time,
            "model": self.model,
            "execution_time": self.execution_time,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["step_name"],
            data["prompt"],
            data["input_data"],
            data["output_data"],
            data["run_id"],
            data["step_run_id"],
            data["run_time"],
            data["status"],
            data["model"],
            data["execution_time"],
        )
