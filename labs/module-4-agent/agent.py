"""AskOps as an agent: a ReAct loop in plain Python, standard library only.

This is the STARTER. It works, but it trusts the model completely. Lab 4.2 breaks it and fixes it.
Run:  python agent.py "your question"
"""
import json, os, sys, urllib.request
from pathlib import Path

# Day 1: nothing is set, so the agent talks to the fake model on your machine.
# Day 2: the sandbox sets LAB_LLM_BASE_URL and LAB_LLM_MODEL, so it talks to the real model.
BASE_URL = os.environ.get("LLM_BASE_URL") or os.environ.get("LAB_LLM_BASE_URL") or "http://127.0.0.1:4000/v1"
MODEL = os.environ.get("LLM_MODEL") or os.environ.get("LAB_LLM_MODEL") or "fake"
API_KEY = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or "none"
MAX_STEPS = 6

DATA = json.loads(Path(__file__).with_name("askops_data.json").read_text())

# ---------------------------------------------------------------- the tools (plain functions)
def search_runbooks(query, service=None):
    if os.environ.get("SEARCH_DOWN"):             # Lab 4.2: pretend the runbook source is down
        return json.dumps([])
    words = {w for w in query.lower().split() if len(w) >= 3}
    hits = [{"id": r["id"], "title": r["title"]} for r in DATA["runbooks"]
            if service in (None, r["service"])
            and words & set(r["title"].lower().split() + r["tags"])]
    return json.dumps(hits[:3])

def get_runbook(runbook_id):
    for r in DATA["runbooks"]:
        if r["id"] == runbook_id:
            return json.dumps(r)
    return f"ERROR: no runbook {runbook_id}. Use search_runbooks first."

def list_incidents():
    return json.dumps(DATA["incidents"])

def open_incident(title, severity, service, runbook_id=None):
    incident = {"id": f"INC-{9001 + len(DATA['incidents'])}", "title": title,
                "severity": severity, "service": service, "runbook_id": runbook_id}
    DATA["incidents"].insert(0, incident)
    return json.dumps(incident)

TOOLS = {"search_runbooks": search_runbooks, "get_runbook": get_runbook,
         "list_incidents": list_incidents, "open_incident": open_incident}

# ---------------------------------------------------------------- what the model reads
def spec(name, description, props=None, required=()):
    return {"type": "function", "function": {"name": name, "description": description,
            "parameters": {"type": "object", "properties": props or {}, "required": list(required)}}}

TOOL_SPECS = [
    spec("search_runbooks", "Find runbooks that match a symptom, such as '502 after deploy'. "
         "Use for how-to-fix questions. Not for open incidents.",
         {"query": {"type": "string"},
          "service": {"type": "string", "enum": ["payments", "auth", "reporting"]}}, ["query"]),
    spec("get_runbook", "Return the steps of one runbook by id, such as 'RB-101'. "
         "Use after search_runbooks. Not for searching.",
         {"runbook_id": {"type": "string"}}, ["runbook_id"]),
    spec("list_incidents", "List the open incidents, newest first."),
    spec("open_incident", "Open a new incident. Only when no open incident covers the problem.",
         {"title": {"type": "string"}, "severity": {"type": "string", "enum": ["low", "medium", "high"]},
          "service": {"type": "string"}, "runbook_id": {"type": "string"}},
         ["title", "severity", "service"]),
]
SYSTEM = ("You are AskOps, an assistant for on-call engineers. Answer only from tool results, "
          "in at most 6 lines. Cite runbook ids. If no tool helps, say so.")

# ---------------------------------------------------------------- the loop
def chat(messages):
    body = json.dumps({"model": MODEL, "messages": messages, "tools": TOOL_SPECS}).encode()
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", body,
                                 {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)

def run(question):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    used = 0
    for step in range(1, MAX_STEPS + 1):
        reply = chat(messages)                                 # reason
        used += reply["usage"]["total_tokens"]
        msg = reply["choices"][0]["message"]
        messages.append(msg)
        if not msg.get("tool_calls"):                          # no action: this is the answer
            return msg["content"], step, used
        for call in msg["tool_calls"]:                         # act
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"] or "{}")
            print(f"  step {step}  ACTION {name}({args})")
            result = TOOLS[name](**args)                       # no checks yet
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})  # observe
    return "Stopped: step budget spent.", step, used

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Payments is returning 502s since the 14:00 release. What do I do?"
    answer, steps, tokens = run(question)
    print(f"\n{answer}\n\n[{steps} steps, {tokens} tokens]")
