class PromptNotFoundException(Exception):
    """Raised when a prompt is not found in the backend."""

    def __init__(self, prompt_id: str):
        self.prompt_id = prompt_id
        super().__init__(f"Prompt with ID {prompt_id} not found.")


class DataNotFoundException(Exception):
    """Raised when data is not found in the backend."""

    def __init__(self, data_id: str):
        self.data_id = data_id
        super().__init__(f"Data with ID {data_id} not found.")
