"""AskOps as an agent: a ReAct loop in plain Python, standard library only.

This is ONE SOLUTION to Lab 4.2: the starter plus five fixes, each marked "Fix".
Run from the module-4-agent folder:  python solutions/agent.py "your question"
"""
import json, os, sys, urllib.request
from pathlib import Path

# Day 1: nothing is set, so the agent talks to the fake model on your machine.
# Day 2: the sandbox sets LAB_LLM_BASE_URL and LAB_LLM_MODEL, so it talks to the real model.
BASE_URL = os.environ.get("LLM_BASE_URL") or os.environ.get("LAB_LLM_BASE_URL") or "http://127.0.0.1:4000/v1"
MODEL = os.environ.get("LLM_MODEL") or os.environ.get("LAB_LLM_MODEL") or "fake"
API_KEY = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or "none"
MAX_STEPS, MAX_TOKENS = 6, 8000                 # Fix 4: a token budget per run

DATA = json.loads((Path(__file__).parent.parent / "askops_data.json").read_text())

# ---------------------------------------------------------------- the tools (plain functions)
def search_runbooks(query, service=None):
    if os.environ.get("SEARCH_DOWN"):             # Lab 4.2: pretend the runbook source is down
        return "ERROR: runbook search is unavailable. Try again later."   # Fix 5: never hide an error
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

# ---------------------------------------------------------------- checks before any tool runs
def run_tool(name, raw_args):
    if name not in TOOLS:                                  # Fix 1: the tool must exist
        return f"ERROR: no tool called {name}. Tools: {', '.join(TOOLS)}."
    try:
        args = json.loads(raw_args or "{}")
        if name == "open_incident":                        # Fix 3: a person approves every write
            answer = input(f"\n  Approve open_incident {args}? [y/N] ").strip().lower()
            if answer != "y":
                return "ERROR: a person refused. Do not open an incident."
        return TOOLS[name](**args)
    except (json.JSONDecodeError, TypeError) as exc:       # Fix 1: arguments must fit the tool
        return f"ERROR: bad arguments for {name}: {exc}"

# ---------------------------------------------------------------- the loop
def chat(messages):
    body = json.dumps({"model": MODEL, "messages": messages, "tools": TOOL_SPECS}).encode()
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", body,
                                 {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"})
    local = "127.0.0.1" in BASE_URL or "localhost" in BASE_URL   # the fake model: skip any proxy
    opener = urllib.request.build_opener(*([urllib.request.ProxyHandler({})] if local else []))
    with opener.open(req, timeout=60) as resp:
        return json.load(resp)

def run(question):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    used, seen = 0, set()
    for step in range(1, MAX_STEPS + 1):
        reply = chat(messages)                                 # reason
        used += reply["usage"]["total_tokens"]
        msg = reply["choices"][0]["message"]
        messages.append(msg)
        if not msg.get("tool_calls"):                          # no action: this is the answer
            return msg["content"], step, used
        for call in msg["tool_calls"]:                         # act
            name, raw_args = call["function"]["name"], call["function"]["arguments"]
            print(f"  step {step}  ACTION {name}({raw_args})")
            if (name, raw_args) in seen:                       # Fix 2: the same call twice is a loop
                return f"Stopped: {name} called twice with the same arguments.", step, used
            seen.add((name, raw_args))
            result = run_tool(name, raw_args)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})  # observe
        if used > MAX_TOKENS:                                  # Fix 4
            return "Stopped: token budget spent.", step, used
    return "Stopped: step budget spent.", step, used

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Payments is returning 502s since the 14:00 release. What do I do?"
    answer, steps, tokens = run(question)
    print(f"\n{answer}\n\n[{steps} steps, {tokens} tokens]")
