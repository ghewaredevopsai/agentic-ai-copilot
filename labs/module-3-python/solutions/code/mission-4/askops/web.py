"""The HTML pages, served by the same app."""
import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from askops import sources
from askops.deps import get_store
from askops.errors import RunbookNotFound
from askops.models import Severity
from askops.schemas import IncidentIn
from askops.store import Store

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, store: Store = Depends(get_store)):
    return templates.TemplateResponse(
        request, "index.html", {"incidents": store.incidents(), "severities": list(Severity)}
    )


@router.get("/ui/ask", response_class=HTMLResponse)
async def ui_ask(request: Request, q: str = "", store: Store = Depends(get_store)):
    if not any(len(w) >= 3 for w in q.split()):
        return templates.TemplateResponse(request, "_results.html", {"q": q, "too_short": True})
    runbooks, incidents = await asyncio.gather(
        sources.runbook_hits(store, q), sources.incident_hits(store, q)
    )
    steps = {h.runbook_id: store.get_runbook(h.runbook_id).steps for h in runbooks}
    return templates.TemplateResponse(
        request, "_results.html", {"q": q, "runbooks": runbooks, "steps": steps, "incidents": incidents}
    )


@router.post("/ui/incidents", response_class=HTMLResponse)
def ui_create_incident(
    request: Request,
    title: str = Form(""),
    severity: str = Form(""),
    service: str = Form(""),
    store: Store = Depends(get_store),
):
    try:
        body = IncidentIn(title=title, severity=severity, service=service)
        incident = store.add_incident(body.title, body.severity, body.service, body.runbook_id)
    except ValidationError as exc:
        message = "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in exc.errors())
        return templates.TemplateResponse(request, "_error_row.html", {"message": message})
    except RunbookNotFound as exc:
        return templates.TemplateResponse(request, "_error_row.html", {"message": str(exc)})
    return templates.TemplateResponse(request, "_incident_row.html", {"i": incident})
