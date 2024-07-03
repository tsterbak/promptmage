"""This module contains the SQLiteBackend class, which is a subclass of the StorageBackend class. It is used to store the data in a SQLite database."""

import json
from loguru import logger
from typing import List, Dict
from sqlalchemy import create_engine, Column, String, Integer, Text, select, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from promptmage.prompt import Prompt
from promptmage.exceptions import PromptNotFoundException
from promptmage.run_data import RunData
from promptmage.storage.storage_backend import StorageBackend

Base = declarative_base()


class PromptModel(Base):
    __tablename__ = "prompts"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    system = Column(Text, nullable=False)
    user = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    template_vars = Column(Text, nullable=False)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "system": self.system,
            "user": self.user,
            "version": self.version,
            "template_vars": self.template_vars.split(","),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PromptModel":
        return cls(
            id=data["id"],
            name=data["name"],
            system=data["system"],
            user=data["user"],
            version=data["version"],
            template_vars=",".join(data["template_vars"]),
        )

    def __repr__(self):
        return f"PromptModel(id={self.id}, name={self.name}, system={self.system}, user={self.user}, version={self.version}, template_vars={self.template_vars})"


class SQLitePromptBackend(StorageBackend):
    """A class that stores the prompts in a SQLite database.

    Attributes:
        db_path (str): The path to the SQLite database. Defaults to ".promptmage/promptmage.db".
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path if db_path else ".promptmage/promptmage.db"
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def store_prompt(self, prompt: Prompt):
        session = self.Session()
        try:
            session.add(PromptModel.from_dict(prompt.to_dict()))
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error storing prompt: {e}")
        finally:
            session.close()

    def update_prompt(self, prompt: Prompt):
        session = self.Session()
        try:
            existing_prompt = (
                session.execute(
                    select(PromptModel).where(PromptModel.name == prompt.name)
                )
                .scalars()
                .all()
            )

            if not existing_prompt:
                raise PromptNotFoundException(
                    f"Prompt with name {prompt.name} not found."
                )

            latest_prompt = max(existing_prompt, key=lambda p: p.version)

            latest_prompt.version += 1
            latest_prompt.system = prompt.system
            latest_prompt.user = prompt.user
            latest_prompt.template_vars = ",".join(prompt.template_vars)

            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating prompt: {e}")
        finally:
            session.close()

    def get_prompt(self, prompt_name: str) -> Prompt:
        session = self.Session()
        try:
            rows = (
                session.execute(
                    select(PromptModel).where(PromptModel.name == prompt_name)
                )
                .scalars()
                .all()
            )
            if not rows:
                raise PromptNotFoundException(
                    f"Prompt with name {prompt_name} not found."
                )
            latest_prompt = max(rows, key=lambda p: p.version)
            return Prompt(**latest_prompt.to_dict())
        finally:
            session.close()

    def get_prompt_by_id(self, prompt_id: str) -> Prompt:
        session = self.Session()
        try:
            prompt = session.execute(
                select(PromptModel).where(PromptModel.id == prompt_id)
            ).scalar_one_or_none()
            if prompt is None:
                raise PromptNotFoundException(f"Prompt with ID {prompt_id} not found.")
            return prompt
        finally:
            session.close()

    def get_prompts(self) -> List[Prompt]:
        session = self.Session()
        try:
            prompts = session.execute(select(PromptModel)).scalars().all()
            return [Prompt(**prompt.to_dict()) for prompt in prompts]
        finally:
            session.close()

    def delete_prompt(self, prompt_id: str):
        session = self.Session()
        try:
            result = session.execute(
                delete(PromptModel).where(PromptModel.id == prompt_id)
            )
            if result.rowcount == 0:
                raise PromptNotFoundException(f"Prompt with ID {prompt_id} not found.")
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting prompt: {e}")
        finally:
            session.close()


class RunDataModel(Base):
    __tablename__ = "data"
    step_run_id = Column(String, primary_key=True)
    run_time = Column(String, nullable=False)
    step_name = Column(String, nullable=False)
    run_id = Column(String)
    status = Column(String, nullable=False)
    prompt = Column(Text)
    input_data = Column(Text)
    output_data = Column(Text)

    def to_dict(self) -> Dict:
        return {
            "step_run_id": self.step_run_id,
            "run_time": self.run_time,
            "step_name": self.step_name,
            "run_id": self.run_id,
            "status": self.status,
            "prompt": Prompt(**json.loads(self.prompt)) if self.prompt else None,
            "input_data": json.loads(self.input_data),
            "output_data": json.loads(self.output_data),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RunDataModel":
        return cls(
            step_run_id=data["step_run_id"],
            run_time=data["run_time"],
            step_name=data["step_name"],
            run_id=data["run_id"],
            status=data["status"],
            prompt=json.dumps(data["prompt"]) if data["prompt"] else None,
            input_data=json.dumps(data["input_data"]),
            output_data=json.dumps(data["output_data"]),
        )

    def __repr__(self):
        return f"RunDataModel(step_run_id={self.step_run_id}, run_time={self.run_time}, step_name={self.step_name}, run_id={self.run_id}, status={self.status}, prompt={self.prompt}, input_data={self.input_data}, output_data={self.output_data})"


class SQLiteDataBackend(StorageBackend):
    """A class that stores the data in a SQLite database.

    Attributes:
        db_path (str): The path to the SQLite database. Defaults to ".promptmage/promptmage.db".
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path if db_path else ".promptmage/promptmage.db"
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def store_data(self, run_data: RunData):
        session = self.Session()
        try:
            session.add(RunDataModel.from_dict(run_data.to_dict()))
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error storing run data: {e}")
        finally:
            session.close()

    def get_data(self, step_run_id: str) -> RunData:
        session = self.Session()
        try:
            run_data = session.execute(
                select(RunDataModel).where(RunDataModel.step_run_id == step_run_id)
            ).scalar_one_or_none()
            if run_data is None:
                return None
            return RunData(**run_data.to_dict())
        finally:
            session.close()

    def get_all_data(self) -> List[RunData]:
        session = self.Session()
        try:
            run_data_list = session.execute(select(RunDataModel)).scalars().all()
            return [RunData(**d.to_dict()) for d in run_data_list]
        finally:
            session.close()
