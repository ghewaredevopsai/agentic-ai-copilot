# CrewAI & Google ADK labs — one support desk, two frameworks

Four labs. You build the Global Bank customer support desk twice: once in CrewAI and once in Google
ADK. Then you measure both and choose one. Nothing is scored, and there is nothing to fill in.

The slides for this module are
[`presentation/CrewAI-GoogleADK.html`](../../presentation/CrewAI-GoogleADK.html).
Each lab follows the part of the slides that it practises.

| Lab | Time | What you do | What you record |
|---|:--:|---|---|
| [1 · Build the triage crew](lab-1-build-the-triage-crew.ipynb) | 25 min | Build a crew of three agents. Run it in order, then with a manager | Requests and tokens, sequential and with a manager. The team each crew chose for GB-T-4471 |
| [2 · What the crew costs](lab-2-what-the-crew-costs.ipynb) | 25 min | Add a critic agent. Then move the workers to a different model | Tokens and `$` for three runs, and whether the critic found anything |
| [3 · The same desk in ADK](lab-3-the-same-desk-in-adk.ipynb) | 25 min | Build the same desk with a runner, a session and named hand-offs | The token total for the three-agent desk |
| [4 · Two frameworks, one task](lab-4-two-frameworks-one-task.ipynb) | 25 min | Run both desks on one ticket. Change what ADK sends. Choose one | The three-row table, and your answers to the five questions |

**Words used in these labs**

- **Agent:** a model with a job description. It can also call tools.
- **Tool:** a Python function that the model can ask to run, for example to look up a ticket.
- **Crew:** CrewAI's word for a group of agents and the tasks they run.
- **Manager:** in CrewAI, an extra model call that decides which agent does which task.
- **Runner and session:** in ADK, the runner runs the agent. The session stores the conversation.
- **Hand-off:** the result one agent passes to the next.
- **Request and token:** a request is one call to the model. A token is the unit a model reads and
  writes, roughly three quarters of an English word.

**The four tickets.** Every lab uses the same four customer tickets. Each belongs to one of four teams
from the Global Bank services you met on Day 1: Accounts, Transactions, Authentication and Customer.
Most runs use `GB-T-4471`, a failed transfer that still debited the customer's account.

## Setup

Open the notebooks in **JupyterLab in your own sandbox**. The model settings are already in the
environment, and CrewAI and Google ADK are already installed. There is nothing to install and no key
to paste.

Run each notebook from top to bottom, one cell at a time. The labs build on each other, so do them in
order.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
