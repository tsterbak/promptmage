"""This module contains the DataStore class, which implements the storage and retrieval of data with different backends."""

from typing import List

from promptmage.storage import StorageBackend
from promptmage.run_data import RunData


class DataStore:
    """A class that stores and retrieves data with different backends."""

    def __init__(self, backend):
        self.backend: StorageBackend = backend

    def store_data(self, data: str):
        """Store data in the backend."""
        self.backend.store_data(data.to_dict())

    def get_data(self) -> List[str]:
        """Retrieve all data from the backend."""
        return RunData.from_dict(self.backend.get_data())
