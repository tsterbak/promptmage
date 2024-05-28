"""This module contains the DataStore class, which implements the storage and retrieval of data with different backends."""

from typing import Dict
from loguru import logger

from promptmage.storage import StorageBackend
from promptmage.run_data import RunData


class DataStore:
    """A class that stores and retrieves data with different backends."""

    def __init__(self, backend):
        self.backend: StorageBackend = backend

    def store_data(self, data: RunData):
        """Store data in the backend."""
        logger.info(f"Storing data: {data}")
        self.backend.store_data(data)

    def get_data(self, run_id: str) -> RunData:
        """Retrieve data from the backend."""
        logger.info(f"Retrieving data with ID: {run_id}")
        return RunData.from_dict(self.backend.get_data(run_id))

    def get_all_data(self) -> Dict:
        """Retrieve all data from the backend."""
        return self.backend.get_all_data()
