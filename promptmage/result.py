class MageResult:

    def __init__(self, next_step: str | None = None, **kwargs):
        self.next_step = next_step
        self.results: dict = kwargs
