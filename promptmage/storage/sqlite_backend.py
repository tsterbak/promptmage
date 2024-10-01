"""This module contains the SQLiteBackend class, which is a subclass of the StorageBackend class. It is used to store the data in a SQLite database."""

import json
import uuid
from loguru import logger
from typing import List, Dict
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Text,
    select,
    delete,
    DateTime,
    ForeignKey,
    Boolean,
    and_,
    Float,
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError

from promptmage.prompt import Prompt
from promptmage.exceptions import PromptNotFoundException
from promptmage.run_data import RunData
from promptmage.storage.storage_backend import StorageBackend

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


def get_next_version(session, name):
    """
    This function retrieves the next version number for a given name.
    """
    max_version = session.execute(
        select(func.max(PromptModel.version)).where(PromptModel.name == name)
    ).scalar()

    if max_version is None:
        return 1
    else:
        return max_version + 1


class PromptModel(Base):
    __tablename__ = "prompts"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    system = Column(Text, nullable=False)
    user = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    template_vars = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False, default=False)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "active": self.active,
            "system": self.system,
            "user": self.user,
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
            active=data["active"],
            template_vars=",".join(data["template_vars"]),
        )

    def __repr__(self):
        return (
            f"PromptModel(id={self.id}, "
            f"name={self.name}, "
            f"active={self.active}, "
            f"system={self.system}, "
            f"user={self.user}, "
            f"version={self.version}, "
            f"template_vars={self.template_vars})"
        )


class SQLitePromptBackend(StorageBackend):
    """A class that stores the prompts in a SQLite database.

    Attributes:
        db_path (str): The path to the SQLite database. Defaults to ".promptmage/promptmage.db".
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path if db_path else ".promptmage/promptmage.db"
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)

        # Define the SQL command to update the existing rows
        # update_command = text("UPDATE prompts SET active = false WHERE active IS NULL")
        # Execute the update command
        # with self.engine.connect() as conn:
        #     conn.execute(update_command)

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
        """Update an existing prompt in the database by id.

        Args:
            prompt (Prompt): The prompt to update.
        """
        session = self.Session()
        try:
            existing_prompt = session.execute(
                select(PromptModel).where(PromptModel.id == prompt.id)
            ).scalar_one_or_none()

            if not existing_prompt:
                raise PromptNotFoundException(
                    f"Prompt with name {prompt.name} and {prompt.id} not found."
                )

            # If changes are made to user prompt and system prompt
            if (
                existing_prompt.system != prompt.system
                or existing_prompt.user != prompt.user
            ):
                new_prompt = PromptModel.from_dict(prompt.to_dict())
                new_prompt.version = get_next_version(session, prompt.name)
                new_prompt.id = generate_uuid()
                if prompt.active:
                    new_prompt.active = True
                    existing_prompt.active = False
                session.add(new_prompt)
            # If made no changes made to user prompt and system prompt
            else:
                existing_prompt.active = prompt.active

            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating prompt: {e}")
        finally:
            session.close()

    def get_prompt(
        self, prompt_name: str, version: int | None = None, active: bool | None = None
    ) -> Prompt:
        """Get a prompt by name from the database.

        Args:
            prompt_name (str): The name of the prompt to retrieve.
            version (int): The version of the prompt to retrieve.
            active (bool): Whether to retrieve only the active prompt.
        """
        session = self.Session()
        try:
            # build the where clause based on name version and active
            where_clause = [PromptModel.name == prompt_name]
            if version is not None:
                where_clause.append(PromptModel.version == version)
            if active is not None:
                where_clause.append(PromptModel.active == active)
            combined_where_clause = and_(*where_clause)
            # run the query to get the prompt
            rows = (
                session.execute(select(PromptModel).where(combined_where_clause))
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
            return Prompt(**prompt.to_dict())
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
    execution_time = Column(Float, nullable=True)
    model = Column(String, nullable=True)
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
            "execution_time": self.execution_time,
            "model": self.model,
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
            execution_time=data["execution_time"],
            model=data["model"],
            prompt=json.dumps(data["prompt"]) if data["prompt"] else None,
            input_data=json.dumps(data["input_data"]),
            output_data=json.dumps(data["output_data"]),
        )

    def __repr__(self):
        return (
            f"RunDataModel(step_run_id={self.step_run_id}, "
            f"run_time={self.run_time}, "
            f"step_name={self.step_name}, "
            f"run_id={self.run_id}, "
            f"status={self.status}, "
            f"prompt={self.prompt}, "
            f"execution_time={self.execution_time}, "
            f"model={self.model}, "
            f"input_data={self.input_data}, "
            f"output_data={self.output_data})"
        )


class EvaluationDatasetModel(Base):
    __tablename__ = "evaluation_datasets"
    id = Column("id", String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())
    datapoints = relationship(
        "EvaluationDatapointModel",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    @classmethod
    def from_dict(cls, data: Dict) -> "EvaluationDatasetModel":
        return cls(
            id=data["id"],
            name=data["name"],
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
        }

    def __repr__(self):
        return f"EvaluationDatasetModel(id={self.id}, name={self.name})"


class EvaluationDatapointModel(Base):
    __tablename__ = "evaluation_datapoints"
    id = Column("id", String, primary_key=True, default=generate_uuid)
    dataset_id = Column(String, ForeignKey("evaluation_datasets.id"))
    dataset = relationship("EvaluationDatasetModel", back_populates="datapoints")
    run_data_id = Column(String, ForeignKey("data.step_run_id"))
    rating = Column(Integer, nullable=True, default=None)

    @classmethod
    def from_dict(cls, data: Dict) -> "EvaluationDatapointModel":
        return cls(
            id=data["id"],
            dataset_id=data["dataset_id"],
            run_data_id=data["run_data_id"],
            rating=data.get("rating"),
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "run_data_id": self.run_data_id,
            "rating": self.rating,
        }

    def __repr__(self):
        return f"EvaluationDatapointModel(id={self.id}, dataset_id={self.dataset_id}, run_data_id={self.run_data_id}, rating={self.rating})"


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

    def create_dataset(self, name: str):
        session = self.Session()
        try:
            dataset = EvaluationDatasetModel(name=name)
            session.add(dataset)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating dataset: {e}")
        finally:
            session.close()

    def delete_dataset(self, dataset_id: str):
        session = self.Session()
        try:
            result = session.execute(
                delete(EvaluationDatasetModel).where(
                    EvaluationDatasetModel.id == dataset_id
                )
            )
            if result.rowcount == 0:
                raise ValueError(f"Dataset with ID {dataset_id} not found.")
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting dataset: {e}")
        finally:
            session.close()

    def add_datapoint_to_dataset(self, datapoint_id, dataset_id):
        session = self.Session()
        try:
            datapoint = EvaluationDatapointModel(
                run_data_id=datapoint_id, dataset_id=dataset_id
            )
            session.add(datapoint)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding datapoint to dataset: {e}")
        finally:
            session.close()

    def get_datasets(self) -> List[EvaluationDatasetModel]:
        session = self.Session()
        try:
            datasets = session.execute(select(EvaluationDatasetModel)).scalars().all()
            logger.info(f"Datasets: {datasets}")
            return [d for d in datasets]
        finally:
            session.close()

    def get_dataset(self, dataset_id: str) -> EvaluationDatasetModel:
        session = self.Session()
        try:
            dataset = session.execute(
                select(EvaluationDatasetModel).where(
                    EvaluationDatasetModel.id == dataset_id
                )
            ).scalar_one_or_none()
            if dataset is None:
                raise ValueError(f"Dataset with ID {dataset_id} not found.")
            return dataset
        finally:
            session.close()

    def get_datapoints(self, dataset_id: str) -> List[EvaluationDatapointModel]:
        session = self.Session()
        try:
            datapoints = (
                session.execute(
                    select(EvaluationDatapointModel).where(
                        EvaluationDatapointModel.dataset_id == dataset_id
                    )
                )
                .scalars()
                .all()
            )
            return [d for d in datapoints]
        finally:
            session.close()

    def get_datapoint(self, datapoint_id: str) -> EvaluationDatapointModel:
        session = self.Session()
        try:
            datapoint = session.execute(
                select(EvaluationDatapointModel).where(
                    EvaluationDatapointModel.id == datapoint_id
                )
            ).scalar_one_or_none()
            if datapoint is None:
                raise ValueError(f"Datapoint with ID {datapoint_id} not found.")
            return datapoint
        finally:
            session.close()

    def rate_datapoint(self, datapoint_id: str, rating: int):
        session = self.Session()
        try:
            datapoint = session.execute(
                select(EvaluationDatapointModel).where(
                    EvaluationDatapointModel.id == datapoint_id
                )
            ).scalar_one_or_none()
            if datapoint is None:
                raise ValueError(f"Datapoint with ID {datapoint_id} not found.")
            datapoint.rating = rating
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error rating datapoint: {e}")
        finally:
            session.close()

    def remove_datapoint_from_dataset(self, datapoint_id: str, dataset_id: str):
        session = self.Session()
        try:
            result = session.execute(
                delete(EvaluationDatapointModel).where(
                    EvaluationDatapointModel.id == datapoint_id
                )
            )
            if result.rowcount == 0:
                raise ValueError(f"Datapoint with ID {datapoint_id} not found.")
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error removing datapoint from dataset: {e}")
        finally:
            session.close()
