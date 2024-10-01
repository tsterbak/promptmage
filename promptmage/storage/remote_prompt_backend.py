import requests
from typing import List
from loguru import logger

from promptmage.prompt import Prompt


class RemotePromptBackend:

    def __init__(self, url: str):
        self.url = url

    def store_prompt(self, prompt: Prompt):
        """Store a prompt in the database."""
        # Send the prompt to the remote server
        try:
            response = requests.post(f"{self.url}/prompts", json=prompt.to_dict())
            response.raise_for_status()
            logger.info(f"Stored prompt {prompt}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to store run data: {e}")
            raise

    def update_prompt(self, prompt: Prompt):
        """Update an existing prompt in the database by id.

        Args:
            prompt (Prompt): The prompt to update.
        """
        try:
            response = requests.put(f"{self.url}/prompts", json=prompt.to_dict())
            response.raise_for_status()
            logger.info(f"Updated prompt {prompt}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update prompt: {e}")
            raise

    def get_prompt(
        self, prompt_name: str, version: int | None = None, active: bool | None = None
    ) -> Prompt:
        """Retrieve a prompt from the database by name or version.

        Args:
            prompt_name (str): The name of the prompt to retrieve.
            version (int | None): The version of the prompt to retrieve.
            active (bool | None): Whether to retrieve only active prompts.

        Returns:
            Prompt: The retrieved prompt.
        """
        logger.info(f"Retrieving prompt with name: {prompt_name}")
        try:
            path = f"{self.url}/prompts/{prompt_name}"
            if version:
                path += f"?version={version}"
            if active:
                path += f"&active={active}"
            response = requests.get(path)
            response.raise_for_status()
            return Prompt(**response.json())
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get prompt: {e}")
            raise

    def get_prompt_by_id(self, prompt_id: str) -> Prompt:
        """Get the prompt by id.

        Args:
            prompt_id (str): The id of the prompt to get.
        """
        logger.info(f"Retrieving prompt with ID {prompt_id}")
        try:
            response = requests.get(f"{self.url}/prompts/id/{prompt_id}")
            response.raise_for_status()
            logger.info(f"{response.json()}")
            return Prompt(**response.json())
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get prompt by id: {e}")
            raise

    def get_prompts(self) -> List[Prompt]:
        """Get all prompts from the database."""
        try:
            response = requests.get(f"{self.url}/prompts")
            response.raise_for_status()
            return [Prompt(**prompt) for prompt in response.json()]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get prompts: {e}")
            raise

    def delete_prompt(self, prompt_id: str):
        """Delete a prompt from the database by id.

        Args:
            prompt_id (str): The id of the prompt to delete.
        """
        try:
            response = requests.delete(f"{self.url}/prompts/{prompt_id}")
            response.raise_for_status()
            logger.info(f"Deleted prompt with id {prompt_id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete prompt: {e}")
            raise
