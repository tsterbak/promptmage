"""This module contains the FileBackend class, which is a subclass of the StorageBackend class. It is used to store the data in a file on the local filesystem."""

from promptmage.storage.storage_backend import StorageBackend


class FileBackend(StorageBackend):
    """A class that stores the data in a file on the local filesystem."""

    def __init__(self, file_path: str):
        self.file_path = file_path
