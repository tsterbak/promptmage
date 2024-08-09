import uuid


class MageResult:

    def __init__(
        self,
        next_step: str | None = None,
        error: str | None = None,
        **kwargs,
    ):
        self.id = str(uuid.uuid4())
        self.next_step = next_step
        self.results: dict = kwargs
        self.error = error

    def __repr__(self):
        return f"<MageResult id={self.id} next_step={self.next_step} results={self.results} error={self.error}>"
