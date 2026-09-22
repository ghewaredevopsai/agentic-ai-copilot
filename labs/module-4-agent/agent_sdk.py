"""The same AskOps agent on the GitHub Copilot SDK. Copilot runs the loop; you give it the tools.

It reuses the tool functions from agent.py, so only the loop changes.
Needs:  pip install github-copilot-sdk     and your Copilot sign-in.
Run:    python agent_sdk.py "your question"
"""
import asyncio, os, sys
from pydantic import BaseModel, Field
from copilot import CopilotClient, ToolSet, define_tool
from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject
from copilot.session_events import (AssistantMessageData, AssistantUsageData,
                                    PermissionRequestCustomTool)
import agent                                                   # the same tools as Lab 4.1

MODEL = os.environ.get("ASKOPS_MODEL", "gpt-5-mini")

def trace(name, args):
    print(f"  ACTION {name}({args})")

class SearchParams(BaseModel):
    query: str = Field(description="Words that describe the symptom")
    service: str | None = Field(None, description="payments, auth or reporting")

class RunbookParams(BaseModel):
    runbook_id: str = Field(description="A runbook id, such as 'RB-101'")

class NoParams(BaseModel):
    pass

class IncidentParams(BaseModel):
    title: str
    severity: str = Field(description="low, medium or high")
    service: str
    runbook_id: str | None = None

# Reads run freely (skip_permission). The write has no skip_permission, so it asks approve() first.
@define_tool(description=agent.TOOL_SPECS[0]["function"]["description"], skip_permission=True)
def search_runbooks(p: SearchParams) -> str:
    trace("search_runbooks", p.model_dump())
    return agent.search_runbooks(p.query, p.service)

@define_tool(description=agent.TOOL_SPECS[1]["function"]["description"], skip_permission=True)
def get_runbook(p: RunbookParams) -> str:
    trace("get_runbook", p.model_dump())
    return agent.get_runbook(p.runbook_id)

@define_tool(description=agent.TOOL_SPECS[2]["function"]["description"], skip_permission=True)
def list_incidents(p: NoParams) -> str:
    trace("list_incidents", {})
    return agent.list_incidents()

@define_tool(description=agent.TOOL_SPECS[3]["function"]["description"])
def open_incident(p: IncidentParams) -> str:
    trace("open_incident", p.model_dump())
    return agent.open_incident(**p.model_dump())

def approve(request, invocation):                              # your code decides
    if isinstance(request, PermissionRequestCustomTool) and request.tool_name == "open_incident":
        if input(f"\n  Approve open_incident {request.args}? [y/N] ").strip().lower() == "y":
            return PermissionDecisionApproveOnce()
        return PermissionDecisionReject(feedback="A person refused. Do not open an incident.")
    return PermissionDecisionReject(feedback="This tool is not allowed.")

async def run(question):
    usage = {"calls": 0, "tokens": 0}
    def on_event(event):
        match event.data:
            case AssistantUsageData() as d:
                usage["calls"] += 1
                usage["tokens"] += (d.input_tokens or 0) + (d.output_tokens or 0)
    async with CopilotClient() as client:
        async with await client.create_session(
                model=MODEL,
                tools=[search_runbooks, get_runbook, list_incidents, open_incident],
                available_tools=ToolSet().add_custom("*"),     # only your tools: no shell, no files
                on_permission_request=approve,
                system_message={"mode": "replace", "content": agent.SYSTEM}) as session:
            session.on(on_event)
            reply = await session.send_and_wait(question, timeout=180)
    answer = reply.data.content if reply and isinstance(reply.data, AssistantMessageData) else "(no answer)"
    return answer, usage

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Payments is returning 502s since the 14:00 release. What do I do?"
    answer, usage = asyncio.run(run(question))
    print(f"\n{answer}\n\n[{usage['calls']} model calls, {usage['tokens']} tokens]")
