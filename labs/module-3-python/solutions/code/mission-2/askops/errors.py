"""The AskOps exception hierarchy."""


class AskOpsError(Exception):
    """Base class for every error AskOps raises on purpose."""


class RunbookNotFound(AskOpsError):
    def __init__(self, runbook_id: str) -> None:
        super().__init__(f"runbook {runbook_id} not found")
        self.runbook_id = runbook_id


class DataError(AskOpsError):
    """A data file is missing or unreadable."""
