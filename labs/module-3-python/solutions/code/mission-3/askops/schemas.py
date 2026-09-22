"""Pydantic models - the shapes the API accepts and returns."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from askops.models import Incident, Runbook, Severity


class RunbookOut(BaseModel):
    id: str
    title: str
    service: str
    tags: list[str]
    steps: list[str]

    @classmethod
    def of(cls, rb: Runbook) -> "RunbookOut":
        return cls(id=rb.id, title=rb.title, service=rb.service, tags=sorted(rb.tags), steps=list(rb.steps))


class IncidentIn(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    severity: Severity
    service: str = Field(min_length=1)
    runbook_id: str | None = None


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    severity: Severity
    service: str
    opened_at: datetime
    runbook_id: str | None


class HitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    runbook_id: str
    title: str
    score: int


class AskOut(BaseModel):
    query: str
    runbooks: list[HitOut]
    incidents: list[IncidentOut]
