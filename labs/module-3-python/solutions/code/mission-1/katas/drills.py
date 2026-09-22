"""Mission 1 - one possible solution. Solve the drills with Copilot first: see solutions/README.md."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path


def word_counts(text: str) -> dict[str, int]:
    return dict(Counter(text.lower().split()))


def unique_services(incidents: list[dict]) -> list[str]:
    return sorted({i["service"] for i in incidents})


def high_severity_titles(incidents: list[dict]) -> list[str]:
    return [i["title"] for i in incidents if i["severity"] == "high"]


def index_by_id(items: list[dict]) -> dict[str, dict]:
    return {item["id"]: item for item in items}


def group_by_service(incidents: list[dict]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for i in incidents:
        groups[i["service"]].append(i["id"])
    return dict(groups)


def first_or_default(items, default=None):
    return next(iter(items), default)


def add_tag(tag: str, tags=None) -> list[str]:
    tags = [] if tags is None else tags
    tags.append(tag)
    return tags


def display_name(user: dict) -> str:
    return user.get("name") or user.get("email") or "anonymous"


def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise ValueError(f"invalid port: {value!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"invalid port: {value!r}")
    return port


def port_or_default(value: str, default: int = 8080) -> int:
    try:
        return parse_port(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def add(self, other: "Money") -> "Money":
        if other.currency != self.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)


@dataclass
class Ticket:
    title: str
    priority: int = 3
    watchers: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 1 <= self.priority <= 4:
            raise ValueError(f"priority must be 1..4, got {self.priority}")


def read_nonblank_lines(path: str | Path) -> list[str]:
    with open(path, encoding="utf-8") as fh:
        stripped = (line.strip() for line in fh)
        return [line for line in stripped if line and not line.startswith("#")]
