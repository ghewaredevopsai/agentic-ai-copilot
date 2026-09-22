"""Keyword search over runbooks."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from askops.store import Store

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Hit:
    runbook_id: str
    title: str
    score: int


def search(store: Store, query: str, limit: int = 5) -> list[Hit]:
    words = {w for w in query.lower().split() if len(w) >= 3}
    if not words:
        raise ValueError("query has no words of 3 or more characters")

    hits = []
    for rb in store.runbooks():
        title_words = set(rb.title.lower().split())
        score = len(words & title_words) + 2 * len(words & rb.tags)
        if score:
            hits.append(Hit(rb.id, rb.title, score))

    hits.sort(key=lambda h: (-h.score, h.runbook_id))
    logger.debug("search q=%r hits=%d", query, len(hits))
    return hits[:limit]
