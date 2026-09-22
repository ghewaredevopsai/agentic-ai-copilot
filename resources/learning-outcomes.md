# Learning Outcomes — Agentic AI & AI-Assisted Development with GitHub Copilot

*From prompt to production agent — one continuous build across three intensive days*
3 days · Intermediate · 8 blocks + capstone

Derived from `course-outline-3day-onepager.html`. Tick a box (`- [x]`) when you
can do the thing without looking it up, not when the slide has been shown. Each block ends with its
lab evidence: tick those only when the lab actually runs and you can show the result.

> **Threaded theme.** Token optimisation and model selection (Block 1.2) is not a one-off — it
> reappears as an outcome in every later block. If those ticks are lagging, the discipline did not
> land, whatever the rest of the sheet says.

## Progress

| Day | Block | Outcomes | Labs | Done |
|-----|-------|:--------:|:----:|:----:|
| 1 | 1.1 · Prompt & Context Engineering | 6 | 4 | ☐ |
| 1 | 1.2 · Token Optimisation & Model Selection | 7 | 4 | ☐ |
| 1 | 1.3 · Python Accelerated with Copilot — the AskOps API | 6 | 5 | ☐ |
| 1 | 1.4 · Agent Foundations, Tool Use & MCP | 6 | 3 | ☐ |
| 2 | 2.1 · LangChain & LangGraph | 6 | 5 | ☐ |
| 2 | 2.2 · Multi-Agent — CrewAI & Google ADK | 6 | 4 | ☐ |
| 2 | 2.3 · RAG, Vector Stores & Agent Memory | 7 | 5 | ☐ |
| 3 | 3.1 · MCP Servers, Production & Kubernetes | 7 | 6 | ☐ |
| 3 | 3.2 · Capstone — Build, Deploy & Demo | 8 | 4 | ☐ |

---

## Day 1 — Direct the Model, Build the App, Give It a Brain

*Own machine · GitHub Copilot · corporate network*

### Block 1.1 · Prompt & Context Engineering

- [ ] Break a prompt into its anatomy and state the output contract it is asking for.
- [ ] Apply the pattern that fits the task — few-shot, chain-of-thought, decomposition, self-critique —
      and say why the other three are wrong for it.
- [ ] Engineer *context*, not just the prompt: decide what the model needs in front of it and what
      is noise.
- [ ] Drive Copilot at depth — `@workspace`, `copilot-instructions.md`, prompt files, agent mode —
      rather than as autocomplete.
- [ ] Compare how different models behave on the same prompt (including Claude) and pick on evidence.
- [ ] Recognise hallucination and drift in a long session, and name what triggered each.

**Lab evidence**

- [ ] Prompt teardown & rewrite — before/after, with the failure named.
- [ ] Schema-valid JSON contract — output parses every time.
- [ ] Your team's instructions file — authored and committed.
- [ ] Break and repair a prompt — you can explain what broke it.

### Block 1.2 · Token Optimisation & Model Selection

- [ ] Account for where tokens actually go: input, output, cached, and the hidden cost of
      conversation history and every tool you enable.
- [ ] Budget a context window deliberately instead of filling it.
- [ ] Say what prompt caching rewards, and what a daily edit to an instructions file costs.
- [ ] Make a task cheaper by design — `max_tokens`, and deterministic code instead of a model call.
- [ ] Choose a model type for a use case against the full grid: quality, latency, cost, context
      length, tool calling, residency.
- [ ] Work Copilot's model picker and AI-credit budget as a deliberate choice, not a default.
- [ ] Route cheap-first with a cascade, and find the gate that pays for itself.

**Lab evidence**

- [ ] Count your own bundle — two bundles measured, and you know what your seat shows about credits.
- [ ] One matrix row — predictions written first, scored against the data, one row you would defend.
- [ ] The cascade — accuracy and cost at four thresholds, including the one that costs more.
- [ ] Token audit — 40%+ cut, with the answer checked after every cut.
- [ ] Delete a model call — the counting done in code, and three runs compared.

### Block 1.3 · Python Accelerated with Copilot — the AskOps API

- [ ] Write the Python this course needs: types, packages, dataclasses, exceptions, logging.
- [ ] Use type hints and pydantic so the model has a contract to code against.
- [ ] Use Copilot as a tutor on unfamiliar code, and spec-first in agent mode on new code.
- [ ] Stand up a FastAPI service and handle async and I/O correctly.
- [ ] Treat tests as the guardrail on AI-written code — the suite is what makes the speed safe.
- [ ] Review an AI suggestion critically and reject it for a stated reason; keep Git history clean.

**Lab evidence**

- [ ] AI-tutored drills — completed.
- [ ] AskOps package & API — built and running locally.
- [ ] pytest suite — green.
- [ ] Accepted a bad suggestion deliberately and caught it with tests.
- [ ] Refactor + PR — raised.

### Block 1.4 · Agent Foundations, Tool Use & MCP

- [ ] Describe the perceive → reason → act → observe loop and locate it in any agent you meet.
- [ ] Implement tool calling from scratch, without a framework hiding it.
- [ ] Write a ReAct loop in ~80 lines of plain Python and explain every line.
- [ ] Set stop conditions and per-run cost control so an agent cannot run away.
- [ ] Decide *agent vs. workflow* for a given problem and defend the cheaper answer.
- [ ] Explain MCP architecture and consume an MCP server from Copilot.

**Lab evidence**

- [ ] Hand-rolled tool-calling agent — working.
- [ ] Made it fail, fixed it, and reported the tokens burned.
- [ ] Drove a real task through MCP inside Copilot.

---

## Day 2 — Frameworks, Teams of Agents, Grounding

*Browser sandbox · OpenCode · guest or personal wifi*

### Block 2.1 · LangChain & LangGraph

- [ ] Work in the sandbox and drive OpenCode as your coding agent.
- [ ] Use LangChain core, LCEL, tools and agents — and say what the abstraction bought you over
      Block 1.4's hand-rolled loop.
- [ ] Model a problem as a LangGraph: state, nodes, conditional routing, cycles.
- [ ] Use checkpointers for session memory, and resume a run that was killed mid-flight.
- [ ] Add a human-in-the-loop interrupt for an action that should require approval.
- [ ] Select a model per node and account for tokens across the graph.

**Lab evidence**

- [ ] Ported the Day-1 agent and diffed the two implementations.
- [ ] Switched OpenCode's model backend and compared the result.
- [ ] Graph with a conditional branch — built.
- [ ] Killed and resumed a run — state survived.
- [ ] Approval interrupt — fires where it should.

### Block 2.2 · Multi-Agent — CrewAI & Google ADK

- [ ] State why you would use multiple agents — and what it costs in tokens, latency and failure modes.
- [ ] Apply the right pattern: sequential, hierarchical, parallel fan-out, critic, router.
- [ ] Build with CrewAI: crews, tasks, delegation.
- [ ] Build the same thing with Google ADK: agents, tools, sessions, runners, evaluation.
- [ ] Choose a framework per scenario from the selection matrix, and mix model tiers across agents.
- [ ] Name the multi-agent anti-patterns and spot one in someone else's design.

**Lab evidence**

- [ ] Crew — built.
- [ ] Rebuilt in ADK — code, traces and spend compared.
- [ ] Added a critic, then smaller worker models, and re-measured.
- [ ] A framework choice justified per scenario, in writing.

### Block 2.3 · RAG, Vector Stores & Agent Memory

- [ ] Choose between retrieval, fine-tuning and long context — with the token economics of each.
- [ ] Pick a chunking strategy and metadata scheme for a real document set.
- [ ] Explain embeddings well enough to debug a retrieval that returns the wrong thing.
- [ ] Use ChromaDB / pgvector, hybrid retrieval and a reranker, and measure the lift each adds.
- [ ] Build agentic RAG — the retriever as a tool the agent decides to call.
- [ ] Implement long-term memory with explicit write and eviction policies.
- [ ] Evaluate retrieval quality with Ragas and act on the score.

**Lab evidence**

- [ ] Three chunking strategies compared on quality *and* tokens per answer.
- [ ] Retriever wired in as an agent tool.
- [ ] Hybrid + rerank — lift measured.
- [ ] Long-term memory persisting across sessions.
- [ ] Ragas run, tuned, re-run — score moved.

---

## Day 3 — Production, Then Yours

*Browser sandbox · per-participant Kubernetes*

### Block 3.1 · MCP Servers, Production & Kubernetes

- [ ] Build your own MCP server wrapping an internal-style API, and register it.
- [ ] Instrument with Langfuse and read a real trace: token spend and cost per trace.
- [ ] Write evals that run as CI gates, including a cost-regression gate.
- [ ] Apply guardrails: PII handling, rate limits, budget caps.
- [ ] Handle failure properly — timeouts, retries, fallback to a cheaper tier.
- [ ] Containerise the agent and deploy it to Kubernetes.
- [ ] Survive a chaos drill and explain what the system did under failure.

**Lab evidence**

- [ ] MCP server built and registered.
- [ ] A real trace read, with cost attributed.
- [ ] Eval suite with a quality threshold *and* a cost ceiling.
- [ ] Guardrails + budget cap enforced.
- [ ] Deployed to the cluster.
- [ ] Chaos drill — run, with the outcome written down.

### Block 3.2 · Capstone — Build, Deploy & Demo

Every participant takes a real internal use case end to end and builds and deploys it themselves.
Tick each requirement when it is demonstrably in your capstone.

- [ ] **Multi-agent orchestration**, with the pattern and framework choice justified.
- [ ] **RAG** over a real document set.
- [ ] **A self-built MCP tool.**
- [ ] **Session + long-term memory.**
- [ ] **Langfuse tracing** in place.
- [ ] **An eval suite** with a quality threshold *and* a cost ceiling.
- [ ] **A justified model choice per agent.**
- [ ] **Running on Kubernetes.**

**Lab evidence**

- [ ] Repository.
- [ ] Architecture note.
- [ ] Evaluation & cost report.
- [ ] Demo delivered, with post-mortem and promotion plan.

---

*The programme is one continuous project, not a list of topics: AskOps is scaffolded on Day 1
morning, given an agent brain by Day 1 evening, rebuilt on production frameworks and grounded in
documents on Day 2, then hardened, deployed and forked for the capstone on Day 3. If a block's
outcomes are ticked but the build did not carry forward, the tick is optimistic.*
