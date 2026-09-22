"""A fake model server for the Module 4 labs. It is not an AI: it replays a script.

It speaks the same chat completions format as a real model server, so agent.py cannot tell
the difference. Each scenario makes the "model" behave in one way, so you can cause a failure
on purpose, every time.

Run:  python fake_llm.py <scenario>      then, in a second terminal:  python agent.py
Scenarios: happy  invented  badargs  loop  write
"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

def call(i, name, args):
    return {"id": f"call_{i}", "type": "function",
            "function": {"name": name, "arguments": json.dumps(args)}}

def act(*calls):
    return {"role": "assistant", "content": None, "tool_calls": list(calls)}

def say(text):
    return {"role": "assistant", "content": text}

def happy(turn, last):
    if turn == 0:
        return act(call(1, "search_runbooks", {"query": "502 after deploy", "service": "payments"}))
    if turn == 1:
        return act(call(2, "get_runbook", {"runbook_id": "RB-101"}), call(3, "list_incidents", {}))
    return say("Follow RB-101: check the deploy pipeline, compare error rates, roll back if the "
               "rate doubled. INC-9001 is already open for this. Add to it; do not open another.")

def invented(turn, last):                  # calls a tool that does not exist
    if turn == 0:
        return act(call(1, "open_ticket", {"summary": "Payments 502s"}))
    return say("I cannot open tickets. Use search_runbooks for the fix: see RB-101.")

def badargs(turn, last):                   # right tool, wrong argument name
    if turn == 0:
        return act(call(1, "get_runbook", {"id": "RB-101"}))
    if turn == 1 and last.startswith("ERROR"):
        return act(call(2, "get_runbook", {"runbook_id": "RB-101"}))
    return say("Follow RB-101: check the deploy pipeline, then roll back if the error rate doubled.")

def loop(turn, last):                      # never learns anything new
    return act(call(turn + 1, "list_incidents", {}))

def write(turn, last):                     # opens a duplicate incident
    if turn == 0:
        return act(call(1, "list_incidents", {}))
    if turn == 1:
        return act(call(2, "open_incident", {"title": "Payments 502s after release", "severity": "high",
                                             "service": "payments", "runbook_id": "RB-101"}))
    if last.startswith("ERROR") or "refused" in last.lower():
        return say("I did not open an incident. INC-9001 already covers this; add to it.")
    return say(f"Opened a new incident: {last}")

SCENARIOS = {"happy": happy, "invented": invented, "badargs": badargs, "loop": loop, "write": write}

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        messages = body["messages"]
        turn = sum(1 for m in messages if m["role"] == "assistant")
        last = next((m["content"] for m in reversed(messages) if m["role"] == "tool"), "") or ""
        message = SCENARIOS[SCENARIO](turn, last)
        prompt_tokens = len(json.dumps(body)) // 4           # a rough estimate: 4 characters a token
        completion_tokens = len(json.dumps(message)) // 4
        print(f"call {turn + 1}: {len(messages)} messages, about {prompt_tokens} tokens in")
        out = {"choices": [{"message": message, "finish_reason": "stop"}],
               "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                         "total_tokens": prompt_tokens + completion_tokens}}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    SCENARIO = sys.argv[1] if len(sys.argv) > 1 else "happy"
    if SCENARIO not in SCENARIOS:
        sys.exit(f"Unknown scenario. Choose one of: {' '.join(SCENARIOS)}")
    print(f"Fake model on http://127.0.0.1:4000/v1, scenario '{SCENARIO}'. Ctrl+C to stop.")
    HTTPServer(("127.0.0.1", 4000), Handler).serve_forever()
