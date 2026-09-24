# CrewAI & Google ADK labs — one support desk, two frameworks

Four labs. You build the Global Bank customer support desk twice: once in CrewAI and once in Google
ADK. The desk clears a queue of five customer tickets. For each one it picks the owning team, writes
the customer's first reply, and writes a handover note for that team. Every lab checks the desk's work
against the right answers. Then you choose a framework. There is nothing to fill in.

The slides for this module are
[`presentation/CrewAI-GoogleADK.html`](../../presentation/CrewAI-GoogleADK.html).
Each lab follows the part of the slides that it practises.

| Lab | Time | What you do | What the desk gains |
|---|:--:|---|---|
| [1 · Clear the queue with a crew](lab-1-clear-the-queue.ipynb) | 25 min | Build a crew of three agents. Make each answer a record. Run the whole queue, then try a manager on the hardest ticket | Every ticket routed, answered and handed over, and checked against the right team |
| [2 · Make every reply safe to send](lab-2-safe-replies.ipynb) | 25 min | Write the bank's rules as code. Add a guardrail that sends an unsafe reply back for a rewrite | No reply promises a refund, gives a deadline or asks for an OTP |
| [3 · The desk in ADK, with the bank's records](lab-3-the-desk-in-adk.ipynb) | 25 min | Build the desk with a runner, a session and named hand-offs. Give it a second tool that reads the account records | Replies that tell the customer what actually happened |
| [4 · Two desks, one queue, one decision](lab-4-two-desks-one-queue.ipynb) | 25 min | Run the best crew and the best ADK desk on the same queue. Change what ADK sends. Choose one | A scorecard for each desk, and your answers to the five questions |

Each lab's Run All takes between one and three minutes.

**Words used in these labs**

- **Agent:** a model with a job description. It can also call tools.
- **Tool:** a Python function that the model can ask to run, for example to look up a ticket.
- **Crew:** CrewAI's word for a group of agents and the tasks they run.
- **Manager:** in CrewAI, an extra model call that decides which agent does which task.
- **Runner and session:** in ADK, the runner runs the agent. The session stores the conversation.
- **Hand-off:** the result one agent passes to the next.
- **Guardrail:** in CrewAI, a check that runs on a task's answer. If the check fails, the agent tries
  again.
- **Handover note:** the note the owning team reads, so it can act without asking the desk again.
- **Request and token:** a request is one call to the model. A token is the unit a model reads and
  writes, roughly three quarters of an English word.

**The queue.** Every lab uses the same five customer tickets, kept in
[`desk_kit.py`](desk_kit.py) with the four teams, the bank's account records and the checks. Each
ticket belongs to one of four teams from the Global Bank services you met on Day 1: Accounts,
Transactions, Authentication and Customer. `GB-T-4475` is the hard one: the customer demands a refund
by tomorrow.

**The checks.** Each lab prints one row per ticket:

- **right team:** the ticket went to the team that owns it.
- **safe reply:** the reply promises no refund, gives no deadline and never asks for an OTP, PIN or
  password.
- **says what happened:** the reply tells the customer something from the bank's records.
- **handover:** all three parts of the handover note have real content.

## Setup

Open the notebooks in **JupyterLab in your own sandbox**. The model settings are already in the
environment, and CrewAI and Google ADK are already installed. There is nothing to install and no key
to paste.

Run each notebook from top to bottom, one cell at a time. The labs build on each other, so do them in
order.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
