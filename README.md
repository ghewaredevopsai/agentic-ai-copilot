# Agentic AI &amp; AI-Assisted Development with GitHub Copilot

A three-day, hands-on course. You start from a prompt and finish with an agent you built,
tested and deployed yourself. Every block is paired with labs.

## The three days

**Day 1 — direct the model, build the app, give it a brain.** On your own machine, with GitHub
Copilot.

| Module | What you learn |
|---|---|
| 1 · Prompt &amp; Context Engineering | The six parts of a request, output contracts, the files Copilot reads for you, grounding, the four common failures, and how to prove one prompt is better than another |
| 2 · Token Optimisation &amp; Model Selection | Where tokens go, context budgeting, caching, and choosing a model per use case |
| 3 · Python Accelerated with Copilot | The Python you need, spec-first building, FastAPI, and tests as the guardrail |
| 4 · Agent Foundations, Tool Use &amp; MCP | Perceive, reason, act, observe. Tool calling, a ReAct loop in plain Python, and MCP |

**Day 2 — frameworks, teams of agents, grounding.** LangChain and LangGraph, multi-agent systems,
and retrieval. In the browser sandbox.

**Day 3 — tracing, evaluation, deployment and your capstone.** You build and deploy your own agent.

## Slides

Open the decks in a browser. No install, and they work offline.

- Module 1: `presentation/module-1-prompt-context-engineering.html`
- Module 2: `presentation/module-2-token-optimization.html`
- Module 3: `presentation/module-3-python-accelerated.html`
- Module 4: `presentation/module-4-agent-foundations.html`
- Module 5: `presentation/module-5-langchain-langgraph.html`
- Day 2 · Module 2 — CrewAI & Google ADK: `presentation/CrewAI-GoogleADK.html`
- Day 2 · Module 3 — RAG, vector stores & memory: `presentation/module-rag-memory.html`

Keys: arrow keys or space to move · `O` for the slide index · `N` for the notes on the current
slide · `F` for full screen. The notes are written for you, not for the trainer, so read them after
the session too.

`course-outline-3day-onepager.html` is the one-page outline of the whole course.

## Labs

The lab guides are in `labs/`. Start with `labs/README.md`, which covers setup.

## What you need on Day 1

- **VS Code** with **GitHub Copilot**, signed in, agent mode enabled
- **JDK 25** and **Maven** &mdash; the Day 1 labs build and test a Spring Boot service
- **Python 3.14**, with `pip` or `uv`, for the later modules. Module 3's labs need access to PyPI for
  `pip install`, so check it works on the corporate network before the course
- **git**, a terminal and a modern browser
- A clone of this course repository in your home folder, so the lab commands find it at
  `~/agentic-ai-copilot`:
  ```bash
  cd ~ && git clone https://github.com/ghewaredevopsai/agentic-ai-copilot.git
  ```
- A clone of the practice repository, **with its tags**:
  ```bash
  git clone https://github.com/brainupgrade-in/global-bank-account
  cd global-bank-account && git fetch --tags --force
  ```
  Each lab starts from a tag, not from `main`. `labs/README.md` says which one and why.
- Day 1 runs on the corporate network, because Copilot only works there. `github.com` must be
  reachable from it.

Days 2 and 3 need a modern browser only. Everything runs in a sandbox the trainer gives you.

## The practice codebase

Global Bank is a double-entry payment posting service. Money moves in balanced pairs: every posting
writes one debit and one credit. The rules that matter are written down in the repository itself,
in `.github/copilot-instructions.md` and `docs/adr/`. You will use them in almost every lab.

One thing to know before you start: the posting service lives on the lab tags, not on `main`.
`main` holds an older account service that predates these rules. Always start a lab from the tag
its guide names.
