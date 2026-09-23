"""AskOps for the Module 5 labs: the Module 4 data and tools, and the sandbox model.

The notebooks in this folder import from here, so each lab shows only what is new.
"""
import copy, json, os
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parent.parent / "module-4-agent" / "askops_data.json").read_text())
RUNBOOKS = DATA["runbooks"]
INCIDENTS = DATA["incidents"]
_INCIDENTS_AT_START = copy.deepcopy(INCIDENTS)


def reset_incidents():
    """Put the incident list back to the three incidents it started with."""
    INCIDENTS[:] = copy.deepcopy(_INCIDENTS_AT_START)


# ---------------------------------------------------------------- the four tools from Module 4
def search_runbooks(query, service=None):
    words = {w for w in query.lower().split() if len(w) >= 3}
    hits = [{"id": r["id"], "title": r["title"]} for r in RUNBOOKS
            if service in (None, r["service"])
            and words & set(r["title"].lower().split() + r["tags"])]
    return json.dumps(hits[:3])


def get_runbook(runbook_id):
    for r in RUNBOOKS:
        if r["id"] == runbook_id:
            return json.dumps(r)
    return f"ERROR: no runbook {runbook_id}. Use search_runbooks first."


def list_incidents():
    return json.dumps(INCIDENTS)


def open_incident(title, severity, service, runbook_id=None):
    """The only tool that WRITES: it adds an incident that other people see."""
    incident = {"id": f"INC-{9001 + len(INCIDENTS)}", "title": title,
                "severity": severity, "service": service, "runbook_id": runbook_id}
    INCIDENTS.insert(0, incident)
    return json.dumps(incident)


# ---------------------------------------------------------------- the same tools, for LangChain
def langchain_tools():
    """The four tools as LangChain tools, the way you write them in Lab 5.1."""
    from typing import Literal
    from langchain.tools import tool

    @tool("search_runbooks")
    def _search(query: str,
                service: Literal["payments", "auth", "reporting"] | None = None) -> str:
        """Find runbooks that match a symptom, such as '502 after deploy'.
        Use for how-to-fix questions. Not for open incidents."""
        return search_runbooks(query, service)

    @tool("get_runbook")
    def _get(runbook_id: str) -> str:
        """Return the steps of one runbook by id, such as 'RB-101'.
        Use after search_runbooks. Not for searching."""
        return get_runbook(runbook_id)

    @tool("list_incidents")
    def _list() -> str:
        """List the open incidents, newest first."""
        return list_incidents()

    @tool("open_incident")
    def _open(title: str, severity: str, service: str, runbook_id: str | None = None) -> str:
        """Open a new incident. severity is low, medium or high.
        Only when no open incident covers the problem."""
        return open_incident(title, severity, service, runbook_id)

    return [_search, _get, _list, _open]


# ---------------------------------------------------------------- the sandbox model
def get_llm(temperature=0):
    """A LangChain chat model for the sandbox model. The sandbox sets everything it needs."""
    from langchain_openai import ChatOpenAI
    base_url = os.environ.get("LAB_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("LAB_LLM_MODEL") or os.environ.get("OPENAI_MODEL")
    if not base_url or not model:
        raise RuntimeError("No model is set up. In a terminal, run: echo $LAB_LLM_MODEL  "
                           "If it prints nothing, tell your trainer.")
    return ChatOpenAI(model=model, base_url=base_url,
                      api_key=os.environ.get("OPENAI_API_KEY", "sandbox"), temperature=temperature)


def trace(result):
    """Print an agent run the way agent.py did on Day 1: ACTION lines, the answer, steps and tokens."""
    steps = tokens = 0
    for m in result["messages"]:
        if m.type == "ai":
            steps += 1
            tokens += (m.usage_metadata or {}).get("total_tokens", 0)
            for c in m.tool_calls:
                print(f"  step {steps}  ACTION {c['name']}({c['args']})")
    print(f"\n{result['messages'][-1].content}\n\n[{steps} steps, {tokens} tokens]")
