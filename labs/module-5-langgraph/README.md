# Module 5 labs — LangChain and LangGraph

**Day 2** · three notebook labs · about 70 minutes · in the browser sandbox

In Module 4 you wrote the AskOps agent by hand. In these labs you rebuild it with LangChain, draw it
as a LangGraph graph, and then give it a memory, a record of every step, and a person's approval
before it writes. Every lab runs on the sandbox model and ends with a real result.

| Lab | Notebook | Time | The result |
|---|---|---|---|
| 5.1 LangChain: rebuild the AskOps agent | `lab-5-1-langchain-askops.ipynb` | 20 min | The agent answers the Lab 4.4 questions, and you compare it with your Day 1 agent |
| 5.2 LangGraph: the AskOps triage graph | `lab-5-2-langgraph-triage.ipynb` | 25 min | Three questions take three paths through your graph, one of them round a cycle |
| 5.3 Memory, approval and resume | `lab-5-3-memory-approval-resume.ipynb` | 25 min | The full agent remembers the conversation and opens an incident only after you approve it |

`askops.py` holds what the notebooks share: the Module 4 runbooks and incidents, the four tools, and
`get_llm()`, which connects to the sandbox model. You do not need to edit it.

## Before you start

Open your sandbox in the browser. It is JupyterLab, and this course is already in it at
`~/work/agentic-ai-copilot`. Open a terminal in JupyterLab and check two things:

```bash
echo "$LAB_LLM_MODEL"
# must print a model name. If it prints nothing, tell your trainer

ls ~/work/agentic-ai-copilot/labs/module-5-langgraph
# must list: README.md  askops.py  and the three lab-5-*.ipynb notebooks
```

## How the labs work

1. Open a notebook from the file panel on the left. Use the **Python 3** kernel.
2. Read each step, then run its cell with **Shift + Enter**.
3. Under each cell, **You should see** says what to expect. Compare it with your output.

There is nothing to fill in and nothing is graded. Read the code before you run it: each cell is
short, and it shows one idea from the deck.

The model is real, so its words change from run to run, and it may call the tools in a different
order. What should stay the same is the shape of the result: which runbook it cites, which path the
graph takes, and whether an incident is opened.

Write your notes in `labs/my-work/lab-5-langgraph.md` in this course folder. That folder is yours,
and you do not commit it.

---

## Lab 5.1 — LangChain: rebuild the AskOps agent

You connect to the model, build a chain with the pipe (`prompt | llm | parser`), turn three AskOps
functions into tools with `@tool`, and build the whole agent with `create_agent`. Then you stop a run
with `recursion_limit`, and stream an answer as it is written.

**Compare with Module 4.** After the last cell, run your fixed Module 4 agent on the same two questions,
in a terminal:

```bash
cd ~/work/agentic-ai-copilot/labs/module-4-agent
python agent.py
python agent.py "Logins are slow this morning. Is there a runbook?"
```

If you did not finish Lab 4.2, its *If you are behind* says how to copy in the solution. Then fill
in this table in your notes:

| | Module 4: `agent.py` | Lab 5.1: `create_agent` |
|---|---|---|
| Tools called, first question | | |
| Steps and tokens, first question | | |
| Where is the loop? | | |
| Where is the step budget? | | |
| Which tools may write? Who decides? | | |

The tokens should be a little lower in Lab 5.1, because Day 1 sent four tool descriptions with every
call and Lab 5.1 sends three. The last row is the same in both columns: your code decides.

## Lab 5.2 — LangGraph: the AskOps triage graph

You first print the graph that `create_agent` built for you in Lab 5.1. Then you see, in a few lines,
why a **reducer** matters: without one, a second node's write silently
replaces the first. Then you write five nodes, each a plain function that returns only what it
changed. Two of them ask the model. You join the nodes with a router and a **cycle**, and stream three
questions through the graph with `stream_mode="updates"`.

Write down the path each question took. Which one went round the cycle, and what stopped it?

## Lab 5.3 — Memory, approval and resume

You add a checkpointer and use two `thread_id` values, to see that one conversation remembers and
the other does not. You read the saved history as an audit trail. You crash a run on purpose and
resume it without repeating work. You pause before `open_incident` with `interrupt()`. Last, you give
the agent all four tools, with `HumanInTheLoopMiddleware` in front of `open_incident`, and decide
yourself whether it may open the incident.

Answer two questions in your notes:

1. A node calls `open_incident`, and then the kernel dies before the node returns. What happens when
   you resume? What does that tell you about where `interrupt()` must go?
2. On Day 1 you approved `open_incident` with an `if` statement while the program waited. What does
   the checkpointer let the approval do that the `if` could not?

---

## If something goes wrong

- **`No model is set up`:** run `echo $LAB_LLM_MODEL` in a terminal. If it prints nothing, tell your
  trainer.
- **A model call times out or returns an error:** run the cell again. The gateway may have been busy.
- **`NameError` for `llm`, `agent` or another name:** you skipped a cell. Run the cells from the top,
  or use **Run** &rarr; **Run All Cells**.
- **Odd results after many runs:** use **Kernel** &rarr; **Restart Kernel and Run All Cells**. The
  incident list starts again with its three incidents.
- **The model gives a different answer from *You should see*:** check the shape, not the words. If the
  path or the runbook is wrong, run the cell again once. Real models vary.

## What you take away

- LangChain replaces the code you wrote on Day 1: prompts, the model call, tool schemas and the loop.
  It sends the same messages, so the Module 4 rules still apply.
- A tool's docstring and type hints are what the model reads.
- `recursion_limit` is your step budget: 2 steps for each round of tool calls, plus 2.
- A node returns only what it changed. The reducer decides how the change joins the state.
- Every cycle needs a stop rule in the state, with a step limit behind it.
- A checkpointer and a `thread_id` give you memory, an audit trail and resume after a crash.
- Put a person's approval in front of any tool that writes. The pause is a saved state. With a
  checkpointer that writes to a database, the answer can come a minute later or the next morning.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
