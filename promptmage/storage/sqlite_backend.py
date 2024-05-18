"""This module contains the SQLiteBackend class, which is a subclass of the StorageBackend class. It is used to store the data in a SQLite database."""

import sqlite3
from typing import List

from promptmage.storage.storage_backend import StorageBackend


class SQLiteBackend(StorageBackend):
    """A class that stores the data in a SQLite database."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()
