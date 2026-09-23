#!/usr/bin/env python3
"""
Generate the Module 5 lab notebooks and their solutions from one source.

Every code cell is declared once. Where the lab and the solution differ, the cell
carries both variants, so a blank can never drift from the answer that grades it.

    python3 gen_labs.py          # writes ../lab-5-N-*.ipynb and ../solutions/

Adapted from the Module 3 generator of the multi-agent workflows course (labs 3.3 and
3.4), moved onto the AskOps data from Module 4 of this course.

Design rules:
  * Graded cells never call the sandbox model. Lab 5.1 grades against a FAKE model that
    replays a script, so a self-check gives the same result every time.
  * Cells marked "Run it for real" call the sandbox model. They are guarded and never
    crash Run All.
  * "BLANK" marks a blank; an unfilled blank raises NameError and prints [TODO].
    NOT three underscores: IPython predefines _, __ and ___ as its output history,
    so under a real kernel that token is a defined empty string, not an undefined name.
  * A blank never sits at module level (NAME = BLANK). It lives inside a function, so
    the NameError happens inside check() and prints [TODO] instead of crashing the cell.
"""
import json, os, pprint

HERE = os.path.dirname(os.path.abspath(__file__))
LABDIR = os.path.abspath(os.path.join(HERE, ".."))
SOLDIR = os.path.join(LABDIR, "solutions")
DATA_FILE = os.path.join(LABDIR, "..", "module-4-agent", "askops_data.json")


class Cell:
    def __init__(self, kind, lab, sol=None):
        self.kind, self.lab, self.sol = kind, lab, (lab if sol is None else sol)


def md(text):
    return Cell("markdown", text)


def code(lab, sol=None):
    return Cell("code", lab, sol)


def to_source(text):
    """nbformat wants a list of lines, each keeping its trailing newline."""
    lines = text.strip("\n").split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]


def build_notebook(cells, solution):
    out = []
    for i, c in enumerate(cells):
        src = c.sol if solution else c.lab
        cell = {"id": f"cell-{i:02d}", "cell_type": c.kind, "metadata": {}, "source": to_source(src)}
        if c.kind == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        out.append(cell)
    return {
        "cells": out,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


# --------------------------------------------------------------------------- #
# shared cells
# --------------------------------------------------------------------------- #
def header(num, title, minutes, bullets, note):
    items = "\n".join("- " + b for b in bullets)
    return md(f"""
# Lab 5.{num} &mdash; {title}

**Time:** about {minutes} min &nbsp;|&nbsp; **Day 2 &middot; Module 5 &mdash; LangChain &amp; LangGraph**

### What you will do
{items}

> **How this lab works.** Fill in every `BLANK`, then run the **Self-check** cell under each
> section. It prints `[PASS]`, `[FAIL]` or `[TODO]` for each check. Graded cells never call the
> sandbox model, so your score does not depend on it. Cells marked **Run it for real** do call
> the model. If it is not reachable, they print how to fix it instead of crashing.

{note}
""")


SETUP_COMMON = '''
# ---------------------------------------------------------------- Setup: run me first
import os, json, copy, textwrap
from typing import Any, Callable

WORK = os.path.join("/tmp", "aac-lab-5-{num}")
os.makedirs(WORK, exist_ok=True)

# ---- self-check plumbing -------------------------------------------------
_results = []

def check(name: str, fn: Callable[[], Any], hint: str = "") -> None:
    """[PASS] / [FAIL] / [TODO] for one check. An unfilled blank prints [TODO]."""
    try:
        ok = bool(fn())
    except NameError:
        print(f"[TODO] {{name}}")
        _results.append(None)
        return
    except Exception as exc:
        print(f"[FAIL] {{name}} -- {{type(exc).__name__}}: {{exc}}")
        _results.append(False)
        return
    print(("[PASS] " if ok else "[FAIL] ") + name + ("" if ok else (" -- " + hint if hint else "")))
    _results.append(ok)

def guard(fn: Callable[[], Any], default: Any = None) -> Any:
    """Run fn(). If a blank above is still unfilled, say so and carry on."""
    try:
        return fn()
    except NameError:
        print("(a blank above is still unfilled -- fill it in, then run this cell again)")
        return default

def score() -> None:
    done = [r for r in _results if r is not None]
    passed = sum(1 for r in done if r)
    todo = sum(1 for r in _results if r is None)
    print(f"\\nScore: {{passed}}/{{len(_results)}}" + (f"   ({{todo}} still TODO)" if todo else ""))

# ---- the sandbox model ---------------------------------------------------
# The sandbox already has a model set up: nothing to install, no key to enter.
LLM_BASE_URL = os.environ.get("LAB_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
LLM_MODEL    = os.environ.get("LAB_LLM_MODEL") or os.environ.get("OPENAI_MODEL")
LLM_API_KEY  = os.environ.get("OPENAI_API_KEY", "sandbox")

def llm_ready() -> bool:
    if not LLM_BASE_URL or not LLM_MODEL:
        print("No model is set up here. In a sandbox terminal run `env | grep LAB_LLM`.")
        print("If it prints nothing, tell your trainer. The graded cells still work.")
        return False
    return True

_llm = None
def get_llm(temperature: float = 0.0):
    """A LangChain chat model that talks to the sandbox model."""
    global _llm
    if _llm is None:
        from langchain_openai import ChatOpenAI
        _llm = ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE_URL,
                          api_key=LLM_API_KEY, temperature=temperature)
    return _llm

def ask(prompt: str, system: str | None = None) -> str:
    """One call to the model. Returns text, or an error string. Never raises."""
    try:
        msgs = ([("system", system)] if system else []) + [("human", prompt)]
        return get_llm().invoke(msgs).content
    except Exception as exc:
        return f"<model unavailable: {{type(exc).__name__}}: {{exc}}>"

print("work dir:", WORK)
print("model   :", LLM_MODEL or "(not set up -- the graded cells still work)")
'''


def setup(num):
    return code(SETUP_COMMON.format(num=num))


with open(DATA_FILE) as fh:
    _DATA = json.load(fh)

DOMAIN = f'''
# ------------------------------------------------- AskOps: the same data and tools as Module 4
# Six runbooks and three open incidents. Nothing here is real, and nothing leaves this notebook.
RUNBOOKS = {pprint.pformat(_DATA["runbooks"], width=100, sort_dicts=False)}

INCIDENTS_AT_START = {pprint.pformat(_DATA["incidents"], width=100, sort_dicts=False)}
INCIDENTS = copy.deepcopy(INCIDENTS_AT_START)

def reset_data():
    """Put the incident list back as it started. The checks call this, so they leave no trace."""
    INCIDENTS[:] = copy.deepcopy(INCIDENTS_AT_START)

# The four AskOps tools from labs/module-4-agent/agent.py, as plain functions.
def search_runbooks(query, service=None):
    words = {{w for w in query.lower().split() if len(w) >= 3}}
    hits = [{{"id": r["id"], "title": r["title"]}} for r in RUNBOOKS
            if service in (None, r["service"])
            and words & set(r["title"].lower().split() + r["tags"])]
    return json.dumps(hits[:3])

def get_runbook(runbook_id):
    for r in RUNBOOKS:
        if r["id"] == runbook_id:
            return json.dumps(r)
    return f"ERROR: no runbook {{runbook_id}}. Use search_runbooks first."

def list_incidents():
    return json.dumps(INCIDENTS)

def open_incident(title, severity, service, runbook_id=None):
    """The only tool that WRITES. It adds a record that other people see."""
    incident = {{"id": f"INC-{{9001 + len(INCIDENTS)}}", "title": title,
                "severity": severity, "service": service, "runbook_id": runbook_id}}
    INCIDENTS.insert(0, incident)
    return json.dumps(incident)

print(len(RUNBOOKS), "runbooks,", len(INCIDENTS), "open incidents")
'''


# =========================================================================== #
# Lab 5.1 -- LangChain: rebuild the AskOps agent
# =========================================================================== #
LAB1 = [
    header(1, "LangChain: rebuild the AskOps agent", 25,
           ["Join a prompt, a model and a parser with the pipe `|`",
            "Turn the AskOps functions into tools, and read the schema LangChain builds",
            "Build the whole agent with one call to `create_agent`",
            "Stop an agent that will not stop, with `recursion_limit`",
            "Run it on the sandbox model and compare it with your Day 1 agent"],
           "> **The same agent as Module 4.** On Day 1 you wrote the loop by hand in `agent.py`.\n"
           "> Here LangChain writes it. Keep your Lab 4.4 notes open: you compare the numbers at the end."),
    setup(1),
    code(DOMAIN),
    code('''
# ------------------------------------------------- a fake model for the graded cells
# It is not an AI. It replays a script of replies, so the checks give the same result every time.
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
import types

class FakeModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):     # a real model sends the tools; the fake ignores them
        return self

def fake(*replies):
    """A fake model that gives these replies, in order. A reply is text, or a tool call."""
    return FakeModel(messages=iter([r if isinstance(r, AIMessage) else AIMessage(r) for r in replies]))

def call(tool, n=1, **args):
    """A scripted tool call, the same shape a real model sends."""
    return AIMessage("", tool_calls=[{"name": tool, "args": args, "id": f"call_{n}"}])

# The plain Module 4 functions, kept under one name so the tools below can call them.
askops = types.SimpleNamespace(search_runbooks=search_runbooks, get_runbook=get_runbook,
                               list_incidents=list_incidents, open_incident=open_incident)
'''),

    md("""
## Concept

Your Day 1 agent did four jobs by hand. LangChain has a ready-made part for each one.

| Day 1, in `agent.py` | LangChain part |
|---|---|
| Build the list of messages | **Prompt template** (`ChatPromptTemplate`) |
| `chat()`: one HTTP POST to the model | **Chat model** (`ChatOpenAI`) |
| Dig the text out of the JSON reply | **Output parser** (`StrOutputParser`) |
| `TOOL_SPECS` and `TOOLS[name](**args)` | **Tool** (`@tool`) |
| The `for` loop and `MAX_STEPS` | **Agent** (`create_agent`) and `recursion_limit` |

The messages that go to the model are the same as on Day 1. Only the amount of code you write changes.
"""),

    md("""
## Section 1 &mdash; A chain: `prompt | model | parser`

The pipe `|` passes the output of one part into the next. The prompt fills its blanks and returns
messages. The model returns an `AIMessage`. The parser takes out the text and returns a plain string.
A fixed set of steps like this, with no tools, is a **chain**.
"""),
    code('''
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an SRE. Answer in one line."),
    ("user", "Summarise this incident: {text}"),
])

def summariser(model):
    """A chain that fills the prompt, calls the model and returns plain text."""
    return BLANK        # TODO: join prompt, model and StrOutputParser() with the pipe |
''', '''
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an SRE. Answer in one line."),
    ("user", "Summarise this incident: {text}"),
])

def summariser(model):
    """A chain that fills the prompt, calls the model and returns plain text."""
    return prompt | model | StrOutputParser()
'''),
    code('''
# --- Self-check: Section 1
check("the prompt fills the {text} blank",
      lambda: "502 after deploy" in prompt.invoke({"text": "502 after deploy"}).to_messages()[1].content)
check("the chain returns plain text, not a message object",
      lambda: isinstance(summariser(fake("Payments: 502 since the deploy.")).invoke({"text": "x"}), str),
      "the parser at the end turns the AIMessage into a str")
check("the chain returns the model's words",
      lambda: summariser(fake("Payments: 502 since the deploy.")).invoke({"text": "x"})
              == "Payments: 502 since the deploy.")
check("batch runs two inputs and returns two answers",
      lambda: sorted(summariser(fake("one", "two")).batch([{"text": "a"}, {"text": "b"}])) == ["one", "two"])
check("the whole chain is a runnable: it has invoke, batch and stream",
      lambda: all(hasattr(summariser(fake("x")), m) for m in ("invoke", "batch", "stream")))
'''),

    md("""
## Section 2 &mdash; Tools: a function plus a docstring

In Module 4 you wrote each tool description by hand, in `TOOL_SPECS`. The `@tool` decorator writes
it for you from three things: the **function name** becomes the tool name, the **type hints** become
the parameters, and the **docstring** becomes the description the model reads.

`open_incident` is left out on purpose. It writes, so it needs a person's approval first. Lab 5.3
adds it safely.
"""),
    code('''
from langchain.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool

def make_tools():
    """The three AskOps READ tools, as LangChain tools."""

    @tool
    def search_runbooks(query: str, service: str | None = None) -> str:
        """Find runbooks that match a symptom, such as '502 after deploy'.
        Use for how-to-fix questions. Not for open incidents."""
        return askops.search_runbooks(query, service)

    @tool
    def get_runbook(runbook_id: BLANK) -> str:     # TODO: the type of runbook_id, such as 'RB-101'
        """Return the steps of one runbook by id, such as 'RB-101'.
        Use after search_runbooks. Not for searching."""
        return askops.get_runbook(runbook_id)

    @tool
    def list_incidents() -> str:
        """List the open incidents, newest first."""
        return askops.list_incidents()

    return [search_runbooks, get_runbook, list_incidents]
''', '''
from langchain.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool

def make_tools():
    """The three AskOps READ tools, as LangChain tools."""

    @tool
    def search_runbooks(query: str, service: str | None = None) -> str:
        """Find runbooks that match a symptom, such as '502 after deploy'.
        Use for how-to-fix questions. Not for open incidents."""
        return askops.search_runbooks(query, service)

    @tool
    def get_runbook(runbook_id: str) -> str:
        """Return the steps of one runbook by id, such as 'RB-101'.
        Use after search_runbooks. Not for searching."""
        return askops.get_runbook(runbook_id)

    @tool
    def list_incidents() -> str:
        """List the open incidents, newest first."""
        return askops.list_incidents()

    return [search_runbooks, get_runbook, list_incidents]
'''),
    code('''
# --- Self-check: Section 2
def _schema(name):
    return next(convert_to_openai_tool(t)["function"] for t in make_tools() if t.name == name)

check("three tools, and open_incident is not one of them",
      lambda: [t.name for t in make_tools()] == ["search_runbooks", "get_runbook", "list_incidents"])
check("the function name became the tool name", lambda: _schema("get_runbook")["name"] == "get_runbook")
check("the type hint became a string parameter",
      lambda: _schema("get_runbook")["parameters"]["properties"]["runbook_id"]["type"] == "string",
      "with no type hint, the model has to guess what to send")
check("runbook_id is required", lambda: _schema("get_runbook")["parameters"]["required"] == ["runbook_id"])
check("the docstring became the description",
      lambda: "Not for searching" in _schema("get_runbook")["description"])
check("a parameter with a default value is optional",
      lambda: _schema("search_runbooks")["parameters"]["required"] == ["query"])
check("the tool still runs the Module 4 function",
      lambda: "RB-101" in next(t for t in make_tools() if t.name == "get_runbook").invoke({"runbook_id": "RB-101"}))
'''),
    code('''
# Read it: what the model receives for get_runbook. Compare it with TOOL_SPECS in agent.py.
guard(lambda: print(json.dumps(_schema("get_runbook"), indent=2)))
'''),

    md("""
## Section 3 &mdash; An agent in one call

`create_agent` runs the whole Module 4 loop. The model asks for a tool, the tool runs, the result goes
back into the messages, and the loop ends when the model replies with no tool call.

Your `MAX_STEPS` is now a setting called `recursion_limit`. It counts **graph steps**, not tool
calls. Each tool call costs 2 steps: the model asks, then the tool runs. Starting and answering cost
2 more. So an agent that may make **N** tool calls needs a limit of **2 &times; N + 2**. When the
limit is reached, the agent raises `GraphRecursionError`.
"""),
    code('''
from langchain.agents import create_agent
from langgraph.errors import GraphRecursionError

SYSTEM = ("You are AskOps, an assistant for on-call engineers. Answer only from tool results, "
          "in at most 6 lines. Cite runbook ids. If no tool helps, say so.")

def build_agent(model):
    """The AskOps agent: the Module 4 loop, built by LangChain."""
    return create_agent(model, tools=BLANK, system_prompt=SYSTEM)   # TODO: the tools from Section 2

def step_limit(tool_calls):
    """The recursion_limit that lets the agent make this many tool calls, and then answer."""
    return BLANK        # TODO: use the rule above
''', '''
from langchain.agents import create_agent
from langgraph.errors import GraphRecursionError

SYSTEM = ("You are AskOps, an assistant for on-call engineers. Answer only from tool results, "
          "in at most 6 lines. Cite runbook ids. If no tool helps, say so.")

def build_agent(model):
    """The AskOps agent: the Module 4 loop, built by LangChain."""
    return create_agent(model, tools=make_tools(), system_prompt=SYSTEM)

def step_limit(tool_calls):
    """The recursion_limit that lets the agent make this many tool calls, and then answer."""
    return 2 * tool_calls + 2
'''),
    code('''
def trace(result):
    """Print a run the way agent.py did: one ACTION line per tool call, then steps and tokens."""
    steps = tokens = 0
    for m in result["messages"]:
        if m.type == "ai":
            steps += 1
            tokens += (m.usage_metadata or {}).get("total_tokens", 0)
            for c in m.tool_calls:
                print(f"  step {steps}  ACTION {c['name']}({c['args']})")
    print(f"\\n{result['messages'][-1].content}\\n\\n[{steps} steps, {tokens} tokens]")

QUESTION = "Payments is returning 502s since the 14:00 release. What do I do?"

def _run(model, limit):
    return build_agent(model).invoke({"messages": [("user", QUESTION)]}, {"recursion_limit": limit})

def _happy():
    return _run(fake(call("search_runbooks", 1, query="502 after deploy"),
                     call("get_runbook", 2, runbook_id="RB-101"),
                     "Follow RB-101: check the last release, then roll back."), 25)

def _three_calls(limit):
    """A fake model that makes three tool calls, then answers."""
    try:
        _run(fake(call("list_incidents", 1), call("list_incidents", 2),
                  call("list_incidents", 3), "done"), limit)
        return "finished"
    except GraphRecursionError:
        return "stopped"

def _loops(limit):
    """A fake model that asks for list_incidents twenty times in a row."""
    try:
        _run(fake(*[call("list_incidents", i) for i in range(20)]), limit)
        return "finished"
    except GraphRecursionError:
        return "stopped"

# The scripted run, printed like Day 1. The fake model reports no tokens, so it shows 0.
guard(lambda: trace(_happy()))
'''),
    code('''
# --- Self-check: Section 3
check("the agent ran both tools and answered",
      lambda: _happy()["messages"][-1].content.startswith("Follow RB-101"))
check("each tool result went back to the model as a message",
      lambda: sum(m.type == "tool" for m in _happy()["messages"]) == 2)
check("the runbook steps reached the model",
      lambda: any(m.type == "tool" and "Roll back" in m.content for m in _happy()["messages"]))
check("step_limit(3) lets three tool calls finish", lambda: _three_calls(step_limit(3)) == "finished")
check("step_limit(3) stops an agent that keeps calling tools",
      lambda: _loops(step_limit(3)) == "stopped",
      "without a limit, a confused model keeps spending tokens")
check("step_limit(3) is the smallest limit that works",
      lambda: _three_calls(step_limit(3) - 1) == "stopped",
      "one step less should stop the same three-call run")
'''),

    md("""
## Run it for real

The same agent on the sandbox model, with the questions from Lab 4.4. Then, in a terminal, run your
Day 1 agent on the same questions (see the lab guide) and compare the ACTION lines, steps and tokens.
"""),
    code('''
QUESTIONS = [QUESTION, "Logins are slow this morning. Is there a runbook?"]

if llm_ready():
    try:
        agent = build_agent(get_llm())
        for q in QUESTIONS:
            print("Q:", q)
            try:
                trace(agent.invoke({"messages": [("user", q)]}, {"recursion_limit": step_limit(5)}))
            except GraphRecursionError:
                print("Stopped: the step limit was reached.")
            print("-" * 70)
    except NameError:
        print("(fill in the blanks above, then run this cell again)")
    except Exception as exc:
        print(f"<agent run failed: {type(exc).__name__}: {exc}>")
'''),
    md("""
### Streaming

`invoke` shows nothing until the end. `stream` with `stream_mode="messages"` gives you the answer
piece by piece while it is written, which is what a chat window needs.
"""),
    code('''
if llm_ready():
    try:
        agent = build_agent(get_llm())
        for token, meta in agent.stream({"messages": [("user", QUESTIONS[1])]},
                                        {"recursion_limit": step_limit(5)}, stream_mode="messages"):
            if meta["langgraph_node"] == "tools":
                print(f"\\n[tool {token.name} returned {len(token.content)} characters]")
            elif token.content:
                print(token.content, end="", flush=True)
        print()
    except NameError:
        print("(fill in the blanks above, then run this cell again)")
    except Exception as exc:
        print(f"<stream failed: {type(exc).__name__}: {exc}>")
'''),
    md("""
### Read it

Look at what moved into LangChain: the loop, the message list, the tool schemas and the step
budget. Look at what stayed yours: **which tools exist**, **what their docstrings say**, and **which
tools may write**. The framework saves typing. It does not decide what your agent may do.

The tokens should be close to your Day 1 numbers, because the same messages go to the model.
If a run chose different tools from last time, that is normal: a real model picks its path at
run time.
"""),
    code('''
score()
'''),
    md("""
## Your turn

1. Change the docstring of `get_runbook` to `"Gets data."`, run **Run it for real** again, and compare
   the ACTION lines. Put the docstring back afterwards. It is the same test as Lab 4.4, Step 4.
2. Run the first question with `step_limit(1)`. What does the engineer see? Write the message your
   agent should show instead of a stack trace.
"""),
]


# =========================================================================== #
# Lab 5.2 -- a StateGraph from scratch
# =========================================================================== #
LAB2_NODES = '''
QUESTION_502  = "Payments returns 502 after deploy"
QUESTION_DOWN = "The auth service is down for everyone"
QUESTION_ODD  = "Something feels odd today"

def fresh(question):
    """A new state for one question."""
    return {"question": question, "kind": None, "findings": [], "tries": 0,
            "steps": 0, "answer": None}

def classify(state: dict) -> dict:
    """Node: is this an outage, or a how-to-fix question?"""
    down = any(w in state["question"].lower() for w in ("down", "outage"))
    return {"kind": "incident" if down else "runbook", "steps": state["steps"] + 1}

def read_incidents(state: dict) -> dict:
    """Node: list the open incidents."""
    ids = [i["id"] for i in json.loads(list_incidents())]
    return {"findings": [f"incidents: {', '.join(ids)}"], "steps": state["steps"] + 1}
'''

LAB2 = [
    header(2, "Build a StateGraph from scratch", 25,
           ["Write nodes that return only the keys they change",
            "Write the reducer that merges those changes into the state",
            "Write the engine: edges, a router and a cycle, in about 40 lines",
            "Add a step budget so the cycle always ends",
            "Run the same nodes on real LangGraph, and stream each step"],
           "> **Why build it first?** LangGraph hides about 40 lines of engine. Once you have written\n"
           "> them, the LangGraph code in the deck and in Lab 5.3 reads as plain Python."),
    setup(2),
    code(DOMAIN),

    md("""
## Concept

A LangGraph graph has four parts:

| Part | What it is |
|---|---|
| **State** | one dictionary that every node can read |
| **Node** | a function: the state goes in, only the **changed keys** come out |
| **Edge** | which node runs next, always |
| **Conditional edge** | which node runs next, decided by a **router** function that reads the state |

A **cycle** is an edge that points back to an earlier node. Here is the AskOps graph you build:

```
classify --runbook--> search --> check --good, or 3 tries--> answer
    |                   ^          |
    |                   +--weak----+
    +--incident--> read_incidents ---------------------------> answer
```
"""),

    md("""
## Section 1 &mdash; Nodes return only what they change

This is the most important rule. A node returns **only the keys it changed**, and the engine merges
them into the state. That keeps each node small and easy to test on its own.
"""),
    code(LAB2_NODES + '''
def search(state: dict) -> dict:
    """Node: search the runbooks for the question. Counts one more try."""
    hits = json.loads(search_runbooks(state["question"]))
    found = ", ".join(h["id"] for h in hits) or "nothing"
    return BLANK        # TODO: the three keys this node changes:
                        #   findings (a one-item list: f"runbooks: {found}"), tries (+1), steps (+1)
''', LAB2_NODES + '''
def search(state: dict) -> dict:
    """Node: search the runbooks for the question. Counts one more try."""
    hits = json.loads(search_runbooks(state["question"]))
    found = ", ".join(h["id"] for h in hits) or "nothing"
    return {"findings": [f"runbooks: {found}"],
            "tries": state["tries"] + 1,
            "steps": state["steps"] + 1}
'''),
    code('''
# --- Self-check: Section 1
_s0 = fresh(QUESTION_502)

check("a node returns only what it changed",
      lambda: set(search(_s0)) == {"findings", "tries", "steps"},
      "returning the whole state makes nodes hard to join together")
check("search records what it found", lambda: "RB-101" in search(_s0)["findings"][0])
check("search counts one more try", lambda: search(_s0)["tries"] == 1)
check("a question with no match says so",
      lambda: search(fresh(QUESTION_ODD))["findings"] == ["runbooks: nothing"])
check("classify sends an outage to the incidents path",
      lambda: classify(fresh(QUESTION_DOWN))["kind"] == "incident")
check("nodes do not change the state they were given",
      lambda: (search(_s0), _s0["tries"] == 0 and _s0["findings"] == [])[1],
      "return a new dict; never edit the state in place")
'''),

    md("""
## Section 2 &mdash; Reducers: how a node's changes join the state

`tries` should be **replaced** by the new value. `findings` should **grow**: every node adds to the
list. That difference is the **reducer**. You declare it once for each key, instead of remembering
it in every node. In LangGraph, `add_messages` is the reducer for the message list.
"""),
    code('''
def replace(old, new):
    return new

def append(old, new):
    return list(old or []) + list(new)

REDUCERS = {
    "findings": append,             # every node's findings are kept, in order
    "kind": replace, "tries": replace, "steps": replace, "answer": replace, "question": replace,
}

def merge(state: dict, update: dict) -> dict:
    """Apply a node's changes, using the reducer declared for each key."""
    out = dict(state)
    for key, value in update.items():
        reducer = REDUCERS.get(key, replace)
        out[key] = BLANK            # TODO: join the old value and the new one with the reducer
    return out
''', '''
def replace(old, new):
    return new

def append(old, new):
    return list(old or []) + list(new)

REDUCERS = {
    "findings": append,             # every node's findings are kept, in order
    "kind": replace, "tries": replace, "steps": replace, "answer": replace, "question": replace,
}

def merge(state: dict, update: dict) -> dict:
    """Apply a node's changes, using the reducer declared for each key."""
    out = dict(state)
    for key, value in update.items():
        reducer = REDUCERS.get(key, replace)
        out[key] = reducer(state.get(key), value)
    return out
'''),
    code('''
# --- Self-check: Section 2
def _a():
    return merge(_s0, {"findings": ["one"], "tries": 1})

def _b():
    return merge(_a(), {"findings": ["two"], "tries": 2})

check("findings grow across nodes", lambda: _b()["findings"] == ["one", "two"],
      "this is the append reducer at work")
check("tries is replaced, not added to a list", lambda: _b()["tries"] == 2)
check("keys a node did not return stay the same", lambda: _b()["question"] == QUESTION_502)
check("the original state is not changed", lambda: _s0["findings"] == [])
check("a key with no reducer is replaced", lambda: merge(_s0, {"novel": 7})["novel"] == 7)
check("two writes to findings both survive",
      lambda: merge(merge(_s0, {"findings": ["x"]}), {"findings": ["y"]})["findings"] == ["x", "y"],
      "with replace, the first write would be lost, with no error")
'''),

    md("""
## Section 3 &mdash; The engine: edges, a router and a cycle

The engine runs a node, merges its changes, and then picks the next node. A **plain edge** always
goes to the same node. A **conditional edge** calls a router. The cycle here is `check` sending a
weak search back to `search`. The engine also has a **step budget**, the same idea as `MAX_STEPS` on
Day 1, so a cycle can never run forever.
"""),
    code('''
END = "__end__"

class Graph:
    def __init__(self):
        self.nodes, self.edges, self.conditions = {}, {}, {}
        self.entry = None

    def add_node(self, name, fn):
        self.nodes[name] = fn
        return self

    def add_edge(self, src, dst):
        self.edges[src] = dst
        return self

    def add_conditional_edge(self, src, router):
        """router(state) returns the name of the next node, or END."""
        self.conditions[src] = router
        return self

    def set_entry(self, name):
        self.entry = name
        return self

    def run(self, state, max_steps=8):
        """Run until END, or until the step budget is spent. Returns (final_state, path)."""
        current, path = self.entry, []
        while current != END:
            if state["steps"] >= max_steps:
                return merge(state, {"answer": "Stopped: step budget spent."}), path
            path.append(current)
            state = merge(state, self.nodes[current](state))
            if current in self.conditions:
                current = self.conditions[current](state)
            else:
                current = BLANK     # TODO: the plain edge out of this node, or END if there is none
        return state, path
''', '''
END = "__end__"

class Graph:
    def __init__(self):
        self.nodes, self.edges, self.conditions = {}, {}, {}
        self.entry = None

    def add_node(self, name, fn):
        self.nodes[name] = fn
        return self

    def add_edge(self, src, dst):
        self.edges[src] = dst
        return self

    def add_conditional_edge(self, src, router):
        """router(state) returns the name of the next node, or END."""
        self.conditions[src] = router
        return self

    def set_entry(self, name):
        self.entry = name
        return self

    def run(self, state, max_steps=8):
        """Run until END, or until the step budget is spent. Returns (final_state, path)."""
        current, path = self.entry, []
        while current != END:
            if state["steps"] >= max_steps:
                return merge(state, {"answer": "Stopped: step budget spent."}), path
            path.append(current)
            state = merge(state, self.nodes[current](state))
            if current in self.conditions:
                current = self.conditions[current](state)
            else:
                current = self.edges.get(current, END)
        return state, path
'''),
    code('''
def check_node(state):
    """Node: nothing to change. The router after it makes the decision."""
    return {"steps": state["steps"] + 1}

def answer(state):
    runbooks = [f for f in state["findings"] if f.startswith("runbooks: RB")]
    if runbooks:
        text = "Follow " + runbooks[-1].split(": ")[1] + "."
    elif state["kind"] == "incident":
        text = "Check the open incidents first: " + state["findings"][-1]
    else:
        text = "No runbook found. Hand over to a person."
    return {"answer": text, "steps": state["steps"] + 1}

def route(state):
    """Router after classify: the kind decides the path."""
    return "search" if state["kind"] == "runbook" else "read_incidents"

def good_enough(state):
    """Router after check: stop when a runbook is found, or after 3 tries."""
    found = any(f.startswith("runbooks: RB") for f in state["findings"])
    return "answer" if found or state["tries"] >= 3 else "search"

def build():
    return (Graph()
            .add_node("classify", classify).add_node("search", search)
            .add_node("check", check_node).add_node("read_incidents", read_incidents)
            .add_node("answer", answer)
            .add_conditional_edge("classify", route)
            .add_edge("search", "check")
            .add_conditional_edge("check", good_enough)
            .add_edge("read_incidents", "answer")
            .add_edge("answer", END)
            .set_entry("classify"))

def _run(question, max_steps=12):
    return build().run(fresh(question), max_steps)

try:
    for q in (QUESTION_502, QUESTION_DOWN, QUESTION_ODD):
        final, path = _run(q)
        print(f"{q}\\n  path  : {' -> '.join(path)}\\n  answer: {final['answer']}\\n")
except NameError:
    print("(fill in the blanks above, then run this cell again)")
'''),
    code('''
# --- Self-check: Section 3
check("a runbook question takes the search path",
      lambda: _run(QUESTION_502)[1] == ["classify", "search", "check", "answer"])
check("it answers with the runbook it found", lambda: "RB-101" in _run(QUESTION_502)[0]["answer"])
check("an outage takes the incidents path",
      lambda: _run(QUESTION_DOWN)[1] == ["classify", "read_incidents", "answer"])
check("a weak search goes round the cycle three times",
      lambda: _run(QUESTION_ODD)[1].count("search") == 3,
      "the router in check sends it back to search until tries reaches 3")
check("after three tries it hands over to a person",
      lambda: "Hand over" in _run(QUESTION_ODD)[0]["answer"])
check("findings from every search are kept", lambda: len(_run(QUESTION_ODD)[0]["findings"]) == 3)
check("a cycle whose router never says stop ends on the budget",
      lambda: "budget" in (Graph()
              .add_node("search", search)
              .add_conditional_edge("search", lambda s: "search")
              .set_entry("search")
              .run(fresh(QUESTION_ODD))[0]["answer"]),
      "a cycle with no budget is an endless loop")
'''),

    md("""
## Run it for real

The same nodes and routers on real LangGraph. Very little changes. `TypedDict` describes the state.
`Annotated[list, add]` is your `append` reducer. `add_conditional_edges` takes your router. And
`recursion_limit` is your step budget.

`stream_mode="updates"` prints each node as it finishes, with only the keys it changed.
"""),
    code('''
try:
    from typing import Annotated
    from typing_extensions import TypedDict
    from operator import add
    from langgraph.graph import StateGraph, START, END as LG_END

    class AskState(TypedDict):
        question: str
        kind: str | None
        findings: Annotated[list, add]       # <- your append reducer, declared once
        tries: int
        steps: int
        answer: str | None

    g = StateGraph(AskState)
    for name, fn in [("classify", classify), ("search", search), ("check", check_node),
                     ("read_incidents", read_incidents), ("answer", answer)]:
        g.add_node(name, fn)
    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", route, {"search": "search", "read_incidents": "read_incidents"})
    g.add_edge("search", "check")
    g.add_conditional_edges("check", good_enough, {"search": "search", "answer": "answer"})
    g.add_edge("read_incidents", "answer")
    g.add_edge("answer", LG_END)
    app = g.compile()

    for update in app.stream(fresh(QUESTION_ODD), {"recursion_limit": 20}, stream_mode="updates"):
        for node, changes in update.items():
            print(f"{node:<15} changed {sorted(changes)}")
    print("\\nanswer:", app.invoke(fresh(QUESTION_502))["answer"])
except ImportError as exc:
    print(f"LangGraph is not installed here ({exc}). The graded cells above do not need it.")
except NameError:
    print("(fill in the blanks above, then run this cell again)")
except Exception as exc:
    print(f"<graph run failed: {type(exc).__name__}: {exc}>")
'''),
    md("""
Now let the sandbox model write the answer. Only the `answer` node changes. The graph, the routers
and the reducer stay the same, so you can test everything except the model's words without a model.
"""),
    code('''
def model_answer(state):
    text = ask("Answer the on-call engineer in at most 3 lines, only from these findings. "
               "Cite runbook ids. If nothing was found, say so.\\n\\nQuestion: " + state["question"]
               + "\\nFindings:\\n" + "\\n".join(state["findings"]))
    return {"answer": text, "steps": state["steps"] + 1}

if llm_ready():
    try:
        g2 = StateGraph(AskState)
        for name, fn in [("classify", classify), ("search", search), ("check", check_node),
                         ("read_incidents", read_incidents), ("answer", model_answer)]:
            g2.add_node(name, fn)
        g2.add_edge(START, "classify")
        g2.add_conditional_edges("classify", route, {"search": "search", "read_incidents": "read_incidents"})
        g2.add_edge("search", "check")
        g2.add_conditional_edges("check", good_enough, {"search": "search", "answer": "answer"})
        g2.add_edge("read_incidents", "answer")
        g2.add_edge("answer", LG_END)
        print(g2.compile().invoke(fresh(QUESTION_502))["answer"])
    except NameError:
        print("(fill in the blanks above, then run this cell again)")
    except Exception as exc:
        print(f"<graph run failed: {type(exc).__name__}: {exc}>")
'''),
    md("""
### Read it

Your `merge` is LangGraph's reducer system. Your `conditions` are `add_conditional_edges`. Your
`max_steps` is `recursion_limit`. What LangGraph adds on top is the hard part: **saving the state
after every node**. That is Lab 5.3.
"""),
    code('''
score()
'''),
    md("""
## Your turn

1. Make `search` and `read_incidents` both run after `classify`, for every question. Which reducer
   must `findings` have so that both results survive? Try it with `replace` and see what you lose.
2. Every node adds 1 to `steps` itself, so a node that forgets makes the budget wrong. Move the
   counting into `Graph.run`. What does a node lose, and what does it gain?
"""),
]


# =========================================================================== #
# Lab 5.3 -- checkpointing: resume, approve, rewind, audit
# =========================================================================== #
LAB3_NODES = '''
QUESTION_502  = "Payments returns 502 after deploy"            # INC-9001 already covers RB-101
QUESTION_DISK = "Disk on the report nodes is at 95 percent"    # RB-302, and no open incident

def fresh(question=QUESTION_DISK):
    """A new state for one question. Also puts the incident list back as it started."""
    reset_data()
    return {"question": question, "findings": [], "runbook_id": None,
            "already_open": False, "steps": 0, "answer": None}

def read_runbooks(s):
    """Node: find the best runbook for the question."""
    hits = json.loads(search_runbooks(s["question"]))
    rid = hits[0]["id"] if hits else None
    return {"findings": [f"runbook: {rid}"], "runbook_id": rid, "steps": s["steps"] + 1}

def read_incidents(s):
    """Node: is an incident for this runbook already open?"""
    covering = [i["id"] for i in json.loads(list_incidents())
                if s["runbook_id"] and i["runbook_id"] == s["runbook_id"]]
    return {"findings": [f"open incidents for it: {covering or 'none'}"],
            "already_open": bool(covering), "steps": s["steps"] + 1}

def service_of(runbook_id):
    return next((r["service"] for r in RUNBOOKS if r["id"] == runbook_id), "unknown")

def file_incident(s):
    """Node: the WRITE. Opens an incident, unless one is already open."""
    if s["already_open"]:
        return {"answer": "An open incident already covers this. Nothing opened.", "steps": s["steps"] + 1}
    opened = json.loads(open_incident(s["question"][:60], "medium", service_of(s["runbook_id"]),
                                      s["runbook_id"]))
    return {"answer": f"Opened {opened['id']}.", "steps": s["steps"] + 1}

def merge(state, update):
    """findings grow; every other key is replaced. The same reducers as Lab 5.2."""
    out = dict(state)
    for k, v in update.items():
        out[k] = list(state.get(k) or []) + list(v) if k == "findings" else v
    return out

END = "__end__"
NODES = {"read_runbooks": read_runbooks, "read_incidents": read_incidents, "file_incident": file_incident}
EDGES = {"read_runbooks": "read_incidents", "read_incidents": "file_incident", "file_incident": END}
'''

LAB3 = [
    header(3, "Checkpointing: resume, approve, rewind, audit", 25,
           ["Write a checkpointer that saves the state after every node",
            "Stop a run in the middle, and resume it without doing work twice",
            "Pause before `open_incident` and wait for a person's approval",
            "Go back to an earlier checkpoint, change one value, and run again",
            "Read the saved states as an audit trail",
            "Do all of it again on real LangGraph, with `interrupt()` and a `thread_id`"],
           "> **It builds on Lab 5.2.** One idea, saving the whole state after every node under a\n"
           "> thread id, gives you all four: resume, approval, rewind and an audit trail."),
    setup(3),
    code(DOMAIN),
    code(LAB3_NODES),

    md("""
## Concept

The AskOps graph in this lab has three nodes, and the last one **writes**:

```
read_runbooks --> read_incidents --> file_incident (opens an incident, unless one is already open)
```

After every node, the engine saves the whole state under a **thread id**. That one idea gives you:

| What you get | How the saved states give it to you |
|---|---|
| **Resume** | start again from the last saved state, not from the beginning |
| **Approval** | save, stop before the write, and continue when a person says yes |
| **Rewind** | load an earlier saved state, change one value, and run from there |
| **Audit trail** | the saved states are a record of what the agent knew at each step |

The audit trail is a **record**, not a summary written by the model. It is what the program really
held at each step.
"""),

    md("""
## Section 1 &mdash; A checkpointer

It only ever adds entries, one list per thread. The real ones in LangGraph work the same way. They
differ mainly in where they save: memory, SQLite or a database.
"""),
    code('''
class Checkpointer:
    """A list of saved states for each thread. It only ever adds."""

    def __init__(self):
        self.threads: dict[str, list[dict]] = {}

    def put(self, thread: str, node: str, state: dict) -> None:
        """Save the state as it is AFTER `node` ran."""
        self.threads.setdefault(thread, []).append(
            {"seq": len(self.threads.get(thread, [])), "after": node,
             "state": json.loads(json.dumps(state))})     # a copy, not a reference

    def latest(self, thread: str) -> dict | None:
        """The most recent checkpoint, or None if the thread is new."""
        history = self.threads.get(thread, [])
        return BLANK                # TODO: the last checkpoint, or None when there is none

    def at(self, thread: str, seq: int) -> dict | None:
        for cp in self.threads.get(thread, []):
            if cp["seq"] == seq:
                return cp
        return None

    def history(self, thread: str) -> list[dict]:
        return list(self.threads.get(thread, []))
''', '''
class Checkpointer:
    """A list of saved states for each thread. It only ever adds."""

    def __init__(self):
        self.threads: dict[str, list[dict]] = {}

    def put(self, thread: str, node: str, state: dict) -> None:
        """Save the state as it is AFTER `node` ran."""
        self.threads.setdefault(thread, []).append(
            {"seq": len(self.threads.get(thread, [])), "after": node,
             "state": json.loads(json.dumps(state))})     # a copy, not a reference

    def latest(self, thread: str) -> dict | None:
        """The most recent checkpoint, or None if the thread is new."""
        history = self.threads.get(thread, [])
        return history[-1] if history else None

    def at(self, thread: str, seq: int) -> dict | None:
        for cp in self.threads.get(thread, []):
            if cp["seq"] == seq:
                return cp
        return None

    def history(self, thread: str) -> list[dict]:
        return list(self.threads.get(thread, []))
'''),
    code('''
# --- Self-check: Section 1
def _cp():
    c = Checkpointer()
    c.put("t1", "read_runbooks", {"steps": 1, "findings": ["a"]})
    c.put("t1", "read_incidents", {"steps": 2, "findings": ["a", "b"]})
    return c

check("a new thread has no checkpoint", lambda: Checkpointer().latest("nope") is None)
check("latest returns the most recent", lambda: _cp().latest("t1")["after"] == "read_incidents")
check("history is in order and complete", lambda: [c["seq"] for c in _cp().history("t1")] == [0, 1])
check("an earlier checkpoint can still be read", lambda: _cp().at("t1", 0)["state"]["steps"] == 1)
def _snapshot_holds():
    c = Checkpointer()
    live = {"steps": 1, "findings": ["a"]}
    c.put("t1", "read_runbooks", live)
    live["findings"].append("changed later")
    return c.latest("t1")["state"]["findings"] == ["a"]
check("a checkpoint is a copy: later changes do not reach it", _snapshot_holds)
'''),

    md("""
## Section 2 &mdash; Resume after a crash

The engine below saves after every node. It can also stop on purpose: `crash_after` pretends the
process died after a node, and `stop_before` pauses before a node. The test is simple: a resumed run
must **continue**, not start again. Here that matters, because starting again would open the
incident twice.
"""),
    code('''
def run_graph(state, thread, cp, max_steps=8, stop_before=None, crash_after=None):
    """Run the graph from the thread's last checkpoint, or from `state` if the thread is new.

    stop_before  -- pause before this node, and wait for approval
    crash_after  -- pretend the process died just after this node
    Returns (state, path, why), where why is done, paused, crashed or budget.
    """
    last = cp.latest(thread)
    current = "read_runbooks"
    if last:
        state, current = last["state"], last["state"].get("__next__", current)

    path = []
    while current != END:
        if state["steps"] >= max_steps:
            return merge(state, {"answer": "Stopped: step budget spent."}), path, "budget"
        if stop_before == current:
            cp.put(thread, "paused", {**state, "__next__": current})
            return state, path, "paused"
        path.append(current)
        state = merge(state, NODES[current](state))
        nxt = EDGES.get(current, END)
        cp.put(thread, current, {**state, "__next__": nxt})
        if crash_after == current:
            return state, path, "crashed"
        current = nxt
    return state, path, "done"

def resume(thread, cp, **kw):
    """Continue a thread from its last checkpoint."""
    last = cp.latest(thread)
    if last is None:
        raise ValueError("nothing to resume")
    return run_graph(BLANK, thread, cp, **kw)     # TODO: which state should a resumed run start from?
''', '''
def run_graph(state, thread, cp, max_steps=8, stop_before=None, crash_after=None):
    """Run the graph from the thread's last checkpoint, or from `state` if the thread is new.

    stop_before  -- pause before this node, and wait for approval
    crash_after  -- pretend the process died just after this node
    Returns (state, path, why), where why is done, paused, crashed or budget.
    """
    last = cp.latest(thread)
    current = "read_runbooks"
    if last:
        state, current = last["state"], last["state"].get("__next__", current)

    path = []
    while current != END:
        if state["steps"] >= max_steps:
            return merge(state, {"answer": "Stopped: step budget spent."}), path, "budget"
        if stop_before == current:
            cp.put(thread, "paused", {**state, "__next__": current})
            return state, path, "paused"
        path.append(current)
        state = merge(state, NODES[current](state))
        nxt = EDGES.get(current, END)
        cp.put(thread, current, {**state, "__next__": nxt})
        if crash_after == current:
            return state, path, "crashed"
        current = nxt
    return state, path, "done"

def resume(thread, cp, **kw):
    """Continue a thread from its last checkpoint."""
    last = cp.latest(thread)
    if last is None:
        raise ValueError("nothing to resume")
    return run_graph(last["state"], thread, cp, **kw)
'''),
    code('''
# --- Self-check: Section 2
def _crash_then_resume():
    cp = Checkpointer()
    s1, p1, why1 = run_graph(fresh(), "t", cp, crash_after="file_incident")
    before = len(INCIDENTS)
    # the process died after the write, but before anyone saw the answer
    s2, p2, why2 = resume("t", cp)
    return p1, why1, p2, why2, s2, before

def _crash_mid():
    cp = Checkpointer()
    run_graph(fresh(), "t", cp, crash_after="read_incidents")
    return resume("t", cp)

check("the run crashes where we said", lambda: _crash_then_resume()[1] == "crashed")
check("the resumed run finishes", lambda: _crash_mid()[2] == "done")
check("the resumed run does NOT repeat finished nodes",
      lambda: _crash_mid()[1] == ["file_incident"],
      "start from the saved state, not from a fresh one")
check("findings from before the crash survived", lambda: len(_crash_mid()[0]["findings"]) == 2)
def _no_double_write():
    p1, why1, p2, why2, s2, before = _crash_then_resume()
    return p2 == [] and before == 4 and len(INCIDENTS) == 4
check("after a crash just after the write, resuming does not write again", _no_double_write,
      "a resumed run that starts again opens a second incident")
'''),

    md("""
## Section 3 &mdash; Pause for approval, and rewind

The same saved states, used in two more ways. `file_incident` writes a record that other people see,
so it is the node that waits for a person. **Rewind** loads an earlier state, changes one value and
runs again. It makes a new branch, and the original history stays as it was.
"""),
    code('''
def approve_and_continue(thread, cp):
    """A person said yes. Continue from where the run paused."""
    return resume(thread, cp)

def rewind(thread, cp, seq, changes: dict):
    """Go back to checkpoint `seq`, apply `changes`, and run again from there.

    Returns the new final state. The original history is left as it was:
    a rewind makes a new branch, it does not erase.
    """
    at = cp.at(thread, seq)
    if at is None:
        raise ValueError(f"no checkpoint {seq}")
    branch = Checkpointer()
    branch.threads[thread] = [c for c in cp.history(thread) if c["seq"] <= seq]
    branch.threads[thread][-1] = {**branch.threads[thread][-1], "state": {**at["state"], **changes}}
    return BLANK                # TODO: resume the thread on `branch`, and return only the final state
''', '''
def approve_and_continue(thread, cp):
    """A person said yes. Continue from where the run paused."""
    return resume(thread, cp)

def rewind(thread, cp, seq, changes: dict):
    """Go back to checkpoint `seq`, apply `changes`, and run again from there.

    Returns the new final state. The original history is left as it was:
    a rewind makes a new branch, it does not erase.
    """
    at = cp.at(thread, seq)
    if at is None:
        raise ValueError(f"no checkpoint {seq}")
    branch = Checkpointer()
    branch.threads[thread] = [c for c in cp.history(thread) if c["seq"] <= seq]
    branch.threads[thread][-1] = {**branch.threads[thread][-1], "state": {**at["state"], **changes}}
    return resume(thread, branch)[0]
'''),
    code('''
# --- Self-check: Section 3
def _paused():
    cp = Checkpointer()
    s, p, why = run_graph(fresh(), "t2", cp, stop_before="file_incident")
    return cp, s, p, why

check("the run pauses before the write", lambda: _paused()[3] == "paused")
check("it paused with both reads done", lambda: _paused()[2] == ["read_runbooks", "read_incidents"])
check("nothing was opened while it waits",
      lambda: (_paused(), len(INCIDENTS) == 3)[1],
      "the point of the pause is that the write has not happened yet")
check("approving continues to the end and opens one incident",
      lambda: approve_and_continue("t2", _paused()[0])[0]["answer"] == "Opened INC-9004.")

def _rewound():
    cp = Checkpointer()
    run_graph(fresh(QUESTION_502), "t3", cp)          # INC-9001 covers it: nothing is opened
    # A person says INC-9001 is a different problem. Go back to after read_incidents (seq 1).
    return cp, rewind("t3", cp, seq=1, changes={"already_open": False})

check("the first run opened nothing", lambda: len(_rewound()[0].history("t3")) == 3
      and "Nothing opened" in _rewound()[0].latest("t3")["state"]["answer"])
check("the rewound run, with one value changed, opens an incident",
      lambda: _rewound()[1]["answer"].startswith("Opened INC-"))
check("the original history is left as it was",
      lambda: len(_rewound()[0].history("t3")) == 3,
      "a rewind makes a new branch; it must not erase what really happened")
'''),

    md("""
## Section 4 &mdash; The audit trail

The history already answers the question *what did the agent know, and when?* This cell prints it.
"""),
    code('''
def audit(thread, cp) -> str:
    """One line per checkpoint: after which node, what was known, and what came next."""
    rows = [f"{'seq':>4}  {'after':<16}{'steps':>6}{'findings':>10}  {'already_open':<14}next"]
    rows.append("-" * 76)
    for c in cp.history(thread):
        s = c["state"]
        rows.append(f"{c['seq']:>4}  {c['after']:<16}{s.get('steps', 0):>6}"
                    f"{len(s.get('findings', [])):>10}  {str(s.get('already_open')):<14}"
                    f"{s.get('__next__', '-')}")
    return "\\n".join(rows)

try:
    _cpx = Checkpointer()
    run_graph(fresh(QUESTION_502), "audit-demo", _cpx)
    print(audit("audit-demo", _cpx))
except NameError:
    print("(finish the sections above, then run this cell again)")
'''),
    code('''
# --- Self-check: Section 4
def _audited():
    c = Checkpointer()
    run_graph(fresh(QUESTION_502), "a1", c)
    return c

check("one line per node, plus a header and a rule",
      lambda: len(audit("a1", _audited()).splitlines()) == 3 + 2)
check("the trail shows findings growing",
      lambda: "         1" in audit("a1", _audited()) and "         2" in audit("a1", _audited()))
check("the trail shows when already_open became true",
      lambda: audit("a1", _audited()).count("True") >= 2)
check("the trail comes from saved states, not from the model",
      lambda: all("state" in c for c in _audited().history("a1")),
      "this is why it is stronger evidence than asking the model what it did")
'''),

    md("""
## Section 5 &mdash; The same, on real LangGraph

Now use LangGraph's own checkpointer. You need three things from the deck:

- `compile(checkpointer=InMemorySaver())` saves the state after every node.
- A `thread_id` in the config files each saved state under one conversation.
- `interrupt(value)` inside a node pauses the run and shows `value` to a person.
  `Command(resume=...)` continues it, and what you pass becomes the return value of `interrupt`.

One thing to remember: when the run continues, the node runs **again from its first line**. So never
put a write before the `interrupt`, or it happens twice.
"""),
    code('''
from typing import Annotated
from typing_extensions import TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END as LG_END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class TicketState(TypedDict):
    question: str
    findings: Annotated[list, add]
    runbook_id: str | None
    already_open: bool
    steps: int
    answer: str | None

def file_incident_approved(s):
    """Node: the WRITE, now behind a person's approval."""
    if s["already_open"]:
        return {"answer": "An open incident already covers this. Nothing opened.", "steps": s["steps"] + 1}
    draft = {"title": s["question"][:60], "severity": "medium",
             "service": service_of(s["runbook_id"]), "runbook_id": s["runbook_id"]}
    decision = BLANK            # TODO: pause here and show the draft to a person: interrupt(draft)
    if decision != "yes":
        return {"answer": "Not approved. Nothing opened.", "steps": s["steps"] + 1}
    opened = json.loads(open_incident(**draft))
    return {"answer": f"Opened {opened['id']}.", "steps": s["steps"] + 1}

def build_lg():
    g = StateGraph(TicketState)
    g.add_node("read_runbooks", read_runbooks)
    g.add_node("read_incidents", read_incidents)
    g.add_node("file_incident", file_incident_approved)
    g.add_edge(START, "read_runbooks")
    g.add_edge("read_runbooks", "read_incidents")
    g.add_edge("read_incidents", "file_incident")
    g.add_edge("file_incident", LG_END)
    return g.compile(checkpointer=InMemorySaver())

def cfg(thread):
    return {"configurable": {"thread_id": thread}}
''', '''
from typing import Annotated
from typing_extensions import TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END as LG_END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class TicketState(TypedDict):
    question: str
    findings: Annotated[list, add]
    runbook_id: str | None
    already_open: bool
    steps: int
    answer: str | None

def file_incident_approved(s):
    """Node: the WRITE, now behind a person's approval."""
    if s["already_open"]:
        return {"answer": "An open incident already covers this. Nothing opened.", "steps": s["steps"] + 1}
    draft = {"title": s["question"][:60], "severity": "medium",
             "service": service_of(s["runbook_id"]), "runbook_id": s["runbook_id"]}
    decision = interrupt(draft)
    if decision != "yes":
        return {"answer": "Not approved. Nothing opened.", "steps": s["steps"] + 1}
    opened = json.loads(open_incident(**draft))
    return {"answer": f"Opened {opened['id']}.", "steps": s["steps"] + 1}

def build_lg():
    g = StateGraph(TicketState)
    g.add_node("read_runbooks", read_runbooks)
    g.add_node("read_incidents", read_incidents)
    g.add_node("file_incident", file_incident_approved)
    g.add_edge(START, "read_runbooks")
    g.add_edge("read_runbooks", "read_incidents")
    g.add_edge("read_incidents", "file_incident")
    g.add_edge("file_incident", LG_END)
    return g.compile(checkpointer=InMemorySaver())

def cfg(thread):
    return {"configurable": {"thread_id": thread}}
'''),
    code('''
# Watch one run: it streams each node, then stops at the interrupt and shows the draft.
try:
    app = build_lg()
    for update in app.stream(fresh(QUESTION_DISK), cfg("eng-a"), stream_mode="updates"):
        for node, changes in update.items():
            print(f"{node:<16}", changes if node == "__interrupt__" else sorted(changes))
    print("\\nwaiting before:", app.get_state(cfg("eng-a")).next)
    print("incidents now :", len(INCIDENTS))
    out = app.invoke(Command(resume="yes"), cfg("eng-a"))
    print("after 'yes'   :", out["answer"], "| incidents now:", len(INCIDENTS))
except NameError:
    print("(fill in the blank above, then run this cell again)")
'''),
    code('''
# --- Self-check: Section 5
def _lg_paused(thread="t-a"):
    app = build_lg()
    first = app.invoke(fresh(QUESTION_DISK), cfg(thread))
    return app, first

check("a question with no open incident pauses at the interrupt",
      lambda: "__interrupt__" in _lg_paused()[1])
check("the person sees the draft incident",
      lambda: _lg_paused()[1]["__interrupt__"][0].value["runbook_id"] == "RB-302")
check("the run waits before file_incident",
      lambda: _lg_paused()[0].get_state(cfg("t-a")).next == ("file_incident",))
check("nothing was opened while it waits", lambda: (_lg_paused(), len(INCIDENTS) == 3)[1])
def _lg_decide(answer):
    app, _ = _lg_paused("t-b")
    return app.invoke(Command(resume=answer), cfg("t-b"))["answer"]
check("'yes' opens exactly one incident",
      lambda: _lg_decide("yes") == "Opened INC-9004." and len(INCIDENTS) == 4)
check("'no' opens nothing", lambda: _lg_decide("no").startswith("Not approved") and len(INCIDENTS) == 3)
check("a covered question never pauses",
      lambda: "__interrupt__" not in build_lg().invoke(fresh(QUESTION_502), cfg("t-c")))
def _two_threads():
    app = build_lg()
    app.invoke(fresh(QUESTION_502), cfg("x"))       # finishes: INC-9001 covers it
    app.invoke(fresh(QUESTION_DISK), cfg("y"))      # pauses at the interrupt
    return app.get_state(cfg("x")).next == () and app.get_state(cfg("y")).next == ("file_incident",)
check("two threads keep separate states", _two_threads)
check("the saved history is the audit trail",
      lambda: len(list(_lg_paused("t-h")[0].get_state_history(cfg("t-h")))) >= 4)
'''),
    code('''
# Resume after a crash, on LangGraph. read_incidents fails once, as if the process died there.
try:
    calls = {"read_runbooks": 0}
    def counting_read_runbooks(s):
        calls["read_runbooks"] += 1
        return read_runbooks(s)
    failed = {"once": False}
    def flaky_read_incidents(s):
        if not failed["once"]:
            failed["once"] = True
            raise RuntimeError("the process died here")
        return read_incidents(s)

    g = StateGraph(TicketState)
    g.add_node("read_runbooks", counting_read_runbooks)
    g.add_node("read_incidents", flaky_read_incidents)
    g.add_edge(START, "read_runbooks")
    g.add_edge("read_runbooks", "read_incidents")
    g.add_edge("read_incidents", LG_END)
    app = g.compile(checkpointer=InMemorySaver())
    try:
        app.invoke(fresh(QUESTION_502), cfg("crash"))
    except RuntimeError as exc:
        print("crashed:", exc, "| waiting before:", app.get_state(cfg("crash")).next)
    out = app.invoke(None, cfg("crash"))       # None means: continue this thread
    print("resumed:", out["findings"])
    print("read_runbooks ran", calls["read_runbooks"], "time(s)")
except Exception as exc:
    print(f"<crash demo failed: {type(exc).__name__}: {exc}>")
'''),

    md("""
## Run it for real

Ask the sandbox model to answer an auditor, using only the audit trail from Section 4. Notice what
it is doing: reading a record, not remembering a run.
"""),
    code('''
if llm_ready():
    try:
        cp = Checkpointer()
        run_graph(fresh(QUESTION_DISK), "real", cp)
        trail = audit("real", cp)
        answer = ask(
            "You are answering an auditor. Using ONLY this execution trail, say what the system knew "
            "when it opened an incident, and whether an incident was already open. If the trail does "
            "not support an answer, say so.\\n\\n" + trail
        )
        print(trail)
        print("\\n--- the answer for the auditor ---\\n" + answer.strip()[:600])
    except NameError:
        print("(finish the sections above, then run this cell again)")
'''),
    md("""
### Read it

The model is summarising a **saved record**. Ask it the same question with no trail, and it writes
something just as confident that nobody can check.

So the honest answer to *can we explain what the agent did?* is: not from the model. From the
checkpoints.
"""),
    code('''
score()
'''),
    md("""
## Your turn

1. `InMemorySaver` loses everything when the kernel restarts. The sandbox also has
   `langgraph-checkpoint-sqlite`. Change `build_lg` to use `SqliteSaver` with a file in `WORK`,
   pause a run, restart the kernel, and resume it.
2. The saved states hold the whole question and every finding. Which fields must never reach a
   checkpoint store under your team's data rules? Where would you remove them: in the node, the
   reducer, or the checkpointer?
"""),
]


LABS = [
    ("lab-5-1-langchain-askops",       LAB1),
    ("lab-5-2-stategraph-from-scratch", LAB2),
    ("lab-5-3-checkpointing",          LAB3),
]


def main():
    os.makedirs(SOLDIR, exist_ok=True)
    for name, cells in LABS:
        for solution, folder in ((False, LABDIR), (True, SOLDIR)):
            path = os.path.join(folder, name + ".ipynb")
            with open(path, "w") as fh:
                json.dump(build_notebook(cells, solution), fh, indent=1)
                fh.write("\n")
            print(("solution " if solution else "lab      ") + os.path.relpath(path, LABDIR))
    print(f"\n{len(LABS)} labs, {len(LABS) * 2} notebooks written")


if __name__ == "__main__":
    main()
