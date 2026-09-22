"""The JSON API, mounted under /api."""
import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from askops import sources
from askops.deps import get_store
from askops.errors import AskOpsError, RunbookNotFound
from askops.schemas import AskOut, HitOut, IncidentIn, IncidentOut, RunbookOut
from askops.store import Store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health(store: Store = Depends(get_store)) -> dict:
    return {"status": "ok", "runbooks": len(store.runbooks())}


@router.get("/runbooks", response_model=list[RunbookOut])
def list_runbooks(service: str | None = None, store: Store = Depends(get_store)):
    return [RunbookOut.of(rb) for rb in store.runbooks(service)]


@router.get("/runbooks/{runbook_id}", response_model=RunbookOut)
def get_runbook(runbook_id: str, store: Store = Depends(get_store)):
    try:
        return RunbookOut.of(store.get_runbook(runbook_id))
    except RunbookNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/incidents", response_model=list[IncidentOut])
def list_incidents(store: Store = Depends(get_store)):
    return store.incidents()


@router.post("/incidents", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(body: IncidentIn, store: Store = Depends(get_store)):
    try:
        return store.add_incident(body.title, body.severity, body.service, body.runbook_id)
    except RunbookNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/ask", response_model=AskOut)
async def ask(
    q: str = Query(min_length=3),
    limit: int = Query(5, ge=1, le=20),
    store: Store = Depends(get_store),
):
    if not any(len(w) >= 3 for w in q.split()):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail="query needs a word of 3+ characters")
    try:
        runbook_hits, incident_hits = await asyncio.gather(
            sources.runbook_hits(store, q, limit),
            sources.incident_hits(store, q),
        )
    except AskOpsError as exc:
        logger.exception("ask failed for q=%r", q)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="search unavailable") from exc
    return AskOut(
        query=q,
        runbooks=[HitOut.model_validate(h) for h in runbook_hits],
        incidents=[IncidentOut.model_validate(i) for i in incident_hits],
    )
