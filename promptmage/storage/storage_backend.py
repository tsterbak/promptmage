"""This module contains the StorageBackend class, which is an abstract class that defines the interface for storage backends."""

from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    """An abstract class that defines the interface for storage backends."""
