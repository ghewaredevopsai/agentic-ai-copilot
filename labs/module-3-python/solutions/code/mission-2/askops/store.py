"""An in-memory store loaded from JSON files."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from askops.errors import DataError, RunbookNotFound
from askops.models import Incident, Runbook, Severity

logger = logging.getLogger(__name__)


class Store:
    def __init__(self, runbooks: dict[str, Runbook], incidents: list[Incident]) -> None:
        self._runbooks = runbooks
        self._incidents = incidents

    @classmethod
    def from_dir(cls, data_dir: str | Path) -> Store:
        data_dir = Path(data_dir)
        runbooks = {rb.id: rb for rb in map(Runbook.from_dict, _read_json(data_dir / "runbooks.json"))}

        incidents: list[Incident] = []
        for raw in _read_json(data_dir / "incidents.json"):
            try:
                incidents.append(Incident.from_dict(raw))
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning("skipping incident %s: %s", raw.get("id", "<no id>"), exc)

        logger.info("loaded %d runbooks and %d incidents from %s", len(runbooks), len(incidents), data_dir)
        return cls(runbooks, incidents)

    def runbooks(self, service: str | None = None) -> list[Runbook]:
        """All runbooks, sorted by id, optionally only one service's."""
        return sorted(
            (rb for rb in self._runbooks.values() if service is None or rb.service == service),
            key=lambda rb: rb.id,
        )

    def get_runbook(self, runbook_id: str) -> Runbook:
        try:
            return self._runbooks[runbook_id]
        except KeyError:
            raise RunbookNotFound(runbook_id) from None

    def incidents(self) -> list[Incident]:
        return sorted(self._incidents, key=lambda i: i.opened_at, reverse=True)

    def add_incident(
        self, title: str, severity: Severity, service: str, runbook_id: str | None = None
    ) -> Incident:
        if runbook_id is not None:
            self.get_runbook(runbook_id)
        next_number = max((int(i.id.removeprefix("INC-")) for i in self._incidents), default=0) + 1
        incident = Incident(
            id=f"INC-{next_number}",
            title=title,
            severity=Severity(severity),
            service=service,
            opened_at=datetime.now(),
            runbook_id=runbook_id,
        )
        self._incidents.append(incident)
        logger.info("opened %s (%s) on %s", incident.id, incident.severity, incident.service)
        return incident


def _read_json(path: Path) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise DataError(f"data file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise DataError(f"invalid JSON in {path}: {exc}") from exc
