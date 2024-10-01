import requests
from loguru import logger
from typing import Any, Dict, List, Optional

from promptmage.run_data import RunData, Prompt


class RemoteDataBackend:
    def __init__(self, url: str):
        self.url = url

    def store_data(self, run_data: RunData):
        """Store the run data."""
        # Send the run data to the remote server
        try:
            response = requests.post(f"{self.url}/runs", json=run_data.to_dict())
            response.raise_for_status()
            logger.info(f"Stored run data: {run_data}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to store run data: {e}")
            raise

    def get_data(self, step_run_id: str) -> RunData:
        """Get the run data for a given step run ID."""
        try:
            response = requests.get(f"{self.url}/runs/{step_run_id}")
            response.raise_for_status()
            run_data = RunData(**response.json())
            run_data.prompt = Prompt(**run_data.prompt)
            return run_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get run data: {e}")
            raise

    def get_all_data(self) -> List[RunData]:
        """Get all the run data."""
        try:
            response = requests.get(f"{self.url}/runs")
            response.raise_for_status()
            run_datas = []
            for data in response.json():
                run_data = RunData(**data)
                run_data.prompt = Prompt(**run_data.prompt)
                run_datas.append(run_data)
            return run_datas
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get all run data: {e}")
            raise

    def create_dataset(self, name: str):
        """Create a new dataset."""
        pass

    def delete_dataset(self, dataset_id: str):
        pass

    def add_datapoint_to_dataset(self, datapoint_id, dataset_id):
        pass

    def get_datasets(self) -> List:
        """Get all the datasets."""
        try:
            response = requests.get(f"{self.url}/datasets")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get all datasets: {e}")
            raise

    def get_dataset(self, dataset_id: str):
        """Get a dataset by ID."""
        try:
            response = requests.get(f"{self.url}/datasets/{dataset_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get dataset: {e}")
            raise

    def get_datapoints(self, dataset_id: str) -> List:
        pass

    def get_datapoint(self, datapoint_id: str):
        pass

    def rate_datapoint(self, datapoint_id: str, rating: int):
        pass

    def remove_datapoint_from_dataset(self, datapoint_id: str, dataset_id: str):
        pass
