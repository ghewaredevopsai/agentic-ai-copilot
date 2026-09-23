# Module 5 labs — LangChain and LangGraph

**Day 2** · Labs 5.1, 5.2 and 5.3 · about 75 minutes · in the browser sandbox ·
Folder: `labs/module-5-langgraph/` in this course folder

In Module 4 you wrote the AskOps agent by hand: a loop in plain Python where you could see every
message. In these labs you rebuild it with LangChain, then give it what the plain loop did not have:
saved state, resume after a crash, and a pause for a person's approval.

- **Lab 5.1** rebuilds the AskOps agent with LangChain: a chain, three tools and `create_agent`. Then
  it runs on the sandbox model, and you compare it with your Day 1 agent.
- **Lab 5.2** builds a small graph engine in plain Python, about 40 lines, then runs the same nodes on
  LangGraph.
- **Lab 5.3** adds a checkpointer. You resume a crashed run, pause before `open_incident` for
  approval, go back to an earlier step, and read the saved states as an audit trail. Then you do the
  same on LangGraph with `interrupt()`.

All three labs use the same AskOps runbooks and incidents as Module 4.

## Words used in these labs

The deck's *Words used in this module* slide has the words from the deck. The ones you need most:

- **Node:** a Python function that reads the state and returns only the keys it changed.
- **Reducer:** the rule for joining a node's change into the state. `findings` grows; most keys are
  replaced.
- **Checkpointer:** saves the whole state after every node. **Thread:** one conversation's saved
  states, found by its `thread_id`.
- **Interrupt:** a pause inside a node that waits for a person. `Command(resume=...)` continues it.

Two more for the labs:

- **Fake model:** in Lab 5.1, the graded cells use a fake model that replays a script. It is not an
  AI. It makes every check give the same result every time.
- **Run it for real:** a cell that calls the sandbox model. These cells are not graded, because a
  real model can choose a different path on each run.

## Before you start

Open your sandbox in the browser. It is JupyterLab, and this course is already in it at
`~/work/agentic-ai-copilot`. Open a terminal in JupyterLab and check two things:

```bash
echo "$LAB_LLM_MODEL"
# must print a model name. If it prints nothing, tell your trainer

ls ~/work/agentic-ai-copilot/labs/module-5-langgraph
# must list: lab-5-1-langchain-askops.ipynb  lab-5-2-stategraph-from-scratch.ipynb
#            lab-5-3-checkpointing.ipynb  solutions  _generators
```

If the folder is missing, tell your trainer. Do not clone the course again by hand.

### How a notebook lab works

1. Open the notebook from the file panel on the left. Use the **Python 3** kernel.
2. Run the first cell, **Setup: run me first**. It prints the model name.
3. Work down the notebook. Each `BLANK` is a gap for you to fill in, with a `# TODO` that says
   what goes there.
4. Under each section, run the **Self-check** cell. It prints one line per check:
   `[PASS]`, `[FAIL]` with a hint, or `[TODO]` if a blank above is still empty.
5. The **score()** cell near the end prints your total, such as `Score: 18/18`.

If a cell prints *a blank above is still unfilled*, fill it in and run the cell again. You can also
use **Run All** at any time. An unfinished lab never crashes. It shows `[TODO]` instead.

Your notes go in `labs/my-work/lab-5-langgraph.md`, in this course folder. That folder is yours, and
you do not commit it.

**Do not open `solutions/` until you finish a lab.** It holds one answer to every blank.

---

## Lab 5.1 — LangChain: rebuild the AskOps agent

**Goal:** see which parts of your Day 1 loop LangChain replaces, and which parts stay yours ·
**Timebox:** 25 min · **Output:** the comparison table in your notes · **Notebook:**
`lab-5-1-langchain-askops.ipynb`

### Step 1 — A chain, and three tools (Sections 1 and 2, 8 min)

In **Section 1**, join the prompt, the model and the parser with the pipe `|`. In **Section 2**, give
`get_runbook` the type hint for `runbook_id`.

**What you should see:** after Section 2, the cell below the self-check prints the schema LangChain
built for `get_runbook`. Put it next to `TOOL_SPECS` in `labs/module-4-agent/agent.py`. It is the
same information, but you did not write any JSON: the function name, type hint and docstring became
the name, the parameters and the description.

### Step 2 — The agent in one call (Section 3, 7 min)

Give `create_agent` the tools, and write `step_limit()`. The rule is in the notebook: each tool call
costs 2 graph steps, and starting and answering cost 2 more.

**What you should see:** the scripted run prints ACTION lines in the same format as your Day 1 agent,
with `0 tokens`, because the fake model reports none. The self-check proves that your limit lets three
tool calls finish, and stops a model that keeps asking for tools.

### Step 3 — Run it for real, and compare (8 min)

Run the **Run it for real** cell. It asks the two questions from Lab 4.4. Then open a terminal and
run your fixed Day 1 agent on the same two questions:

```bash
cd ~/work/agentic-ai-copilot/labs/module-4-agent
python my_agent.py
python my_agent.py "Logins are slow this morning. Is there a runbook?"
```

If you do not have `my_agent.py`, Lab 4.4, Step 1 says how to make it from the solution.

Fill in this table in your notes:

| | Day 1: `my_agent.py` | Lab 5.1: `create_agent` |
|---|---|---|
| Tools called, question 1 | | |
| Steps and tokens, question 1 | | |
| Where is the loop? | | |
| Where is the step budget? | | |
| Which tools may write? Who decides? | | |

**What you should see:** the tokens are close, because the same messages go to the model. The tools
may differ from run to run, which is normal for a real model. The last row is the same in both
columns: your code decides.

### Step 4 — Streaming (2 min)

Run the **Streaming** cell. The answer appears piece by piece, and a line marks each tool result.
This is `stream_mode="messages"` from the deck.

### If you are behind

Skip Step 4, and fill in only the first and last rows of the table.

---

## Lab 5.2 — Build a StateGraph from scratch

**Goal:** write the 40 lines LangGraph hides, so the LangGraph code in Lab 5.3 reads as plain Python ·
**Timebox:** 25 min · **Output:** a score in the notebook, and one answer in your notes ·
**Notebook:** `lab-5-2-stategraph-from-scratch.ipynb`

The graph sends a how-to-fix question to `search`, and an outage to `read_incidents`. After a
search, `check` either goes on to `answer` or sends the question back to `search`. That is the cycle.

### Step 1 — A node that returns only what it changed (Section 1, 5 min)

Fill in what `search` returns: three keys, not the whole state.

**What you should see:** the check *nodes do not change the state they were given* passes. A node
that edits the state in place, or returns all of it, is the most common first bug in LangGraph.

### Step 2 — The reducer (Section 2, 5 min)

Fill in one line of `merge`: join the old value and the new one with the key's reducer.

**What you should see:** `findings` grows from node to node, and `tries` is replaced. The last check
shows what `replace` would do to two writes: one of them would be lost, with no error.

### Step 3 — The engine and the cycle (Section 3, 8 min)

Fill in the plain edge in `Graph.run`. Then read the printed paths for the three questions.

**What you should see:**

- *Payments returns 502 after deploy* goes `classify -> search -> check -> answer`, with RB-101.
- *The auth service is down* goes `classify -> read_incidents -> answer`.
- *Something feels odd today* goes round `search -> check` three times, then hands over to a person.

The last self-check builds a cycle that never stops, and shows that the step budget ends it.

### Step 4 — Run it for real (5 min)

Run the LangGraph cell. It uses **your** nodes and routers. It streams one line per node with
`stream_mode="updates"`, showing only the keys that node changed. Then run the next cell, where the
sandbox model writes the answer from the findings.

Write one line in your notes: which three parts of your engine became `Annotated[list, add]`,
`add_conditional_edges` and `recursion_limit`?

### If you are behind

Do Steps 1 to 3 only. The LangGraph cell in Lab 5.3 shows the same ideas.

---

## Lab 5.3 — Checkpointing: resume, approve, rewind, audit

**Goal:** see how one idea, saving the state after every node, gives you resume, approval, rewind and
an audit trail · **Timebox:** 25 min · **Output:** a score in the notebook, and two answers in your
notes · **Notebook:** `lab-5-3-checkpointing.ipynb`

The graph here has three nodes: `read_runbooks`, `read_incidents` and `file_incident`. The last one
**writes**: it opens an incident, unless one is already open for that runbook. Two questions run all
the way through the lab:

- *Payments returns 502 after deploy* finds RB-101. INC-9001 already covers it, so nothing is opened.
- *Disk on the report nodes is at 95 percent* finds RB-302. No incident covers it, so it opens one.

### Step 1 — The checkpointer and resume (Sections 1 and 2, 7 min)

Fill in `latest()`, then the state that `resume()` starts from.

**What you should see:** a run that crashes after `read_incidents` resumes with only
`file_incident` left to do. The last check crashes the run just after the write, then resumes. It
must not open a second incident. Starting again from the beginning would.

### Step 2 — Approval and rewind (Section 3, 5 min)

Fill in the last line of `rewind()`.

**What you should see:** the run pauses before `file_incident`, and the incident count stays at 3
until you approve. The rewind goes back to the 502 run, pretends INC-9001 is a different problem,
and runs again from there. This time it opens an incident, and the original history is unchanged.

### Step 3 — The audit trail (Section 4, 3 min)

Run the cell and read the table. Each line is one saved state: after which node, how many findings,
and what came next.

### Step 4 — The same on LangGraph (Section 5, 8 min)

Fill in the one blank in `file_incident_approved`: pause with `interrupt(draft)`.

**What you should see:** the watch cell streams two nodes, then an `__interrupt__` line with the
draft incident. The incident count stays at 3. After `Command(resume="yes")` it is 4. The self-check
also shows that `"no"` opens nothing, that two `thread_id` values keep separate states, and that the
saved history is your audit trail. The crash cell shows LangGraph's resume: `invoke(None, config)`
continues the thread, and `read_runbooks` does not run again.

In your notes, answer two questions:

1. Why must `interrupt()` come **before** `open_incident` in the node, never after it?
2. Your Day 1 agent asked for approval with an `if` statement while the program waited. What does
   the checkpointer let the approval do that the `if` could not?

### Step 5 — Run it for real (2 min)

The sandbox model answers an auditor using only the audit trail. Read its answer against the table
from Step 3.

### If you are behind

Do Steps 1 and 4. They are the two ideas you need for the capstone on Day 3.

---

## What you take away

- LangChain replaces the code you wrote on Day 1: prompts, the model call, parsing, tool schemas
  and the loop. It sends the same messages, so the Module 4 rules still apply.
- A tool's docstring and type hints are what the model reads. Write them with care.
- `recursion_limit` is your step budget: 2 steps per tool call, plus 2.
- A node returns only what it changed. The reducer decides how that change joins the state.
- Every cycle needs a stop rule in the state, and a step budget behind it.
- A checkpointer and a `thread_id` give you memory, resume after a crash, and an audit trail.
- Put `interrupt()` before any tool that writes. The pause is a saved state, so a person can answer
  a minute later or the next morning.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
