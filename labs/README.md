# Labs — how they work, and the one-time setup

| Day | Guide | Labs |
|---|---|---|
| 1 | [Module 1 — Prompt & context engineering](module-1-labs.md) | 1 · 2 · 3 · 4 |
| 1 | [Module 2 — Token optimisation & model selection](module-2-tokens/README.md) | 0 · 1 · 2 · 3 · 4 |
| 1 | [Module 3 — Python Accelerated with Copilot](module-3-python/README.md) | 0 · 1 · 2 · 3 · 4 · 5 |
| 2 | [Module 4 — Agent foundations and tool use](module-4-agent/README.md) | 4.1 · 4.2 · 4.3 · 4.4 |
| 2 | [Module 5 — LangChain and LangGraph](module-5-langgraph/README.md) | 5.1 · 5.2 · 5.3 |
| 2 | [RAG, vector stores and agent memory](module-rag-memory/README.md) | R.1 · R.2 · R.3 |
| 2 | [Module 2 — CrewAI & Google ADK](CrewAI-GoogleADK/README.md) | 1 · 2 · 3 · 4 |

Module 2 uses the same `global-bank-account` clone at `m3-start`, plus a small setup of its own: see
[`module-2-tokens/README.md`](module-2-tokens/README.md). Module 3 has its own practice app, AskOps,
and its own setup: see [`module-3-python/README.md`](module-3-python/README.md). Module 4 works in
`module-4-agent/`, and its guide and setup are in
[`module-4-agent/README.md`](module-4-agent/README.md). The rest of this page is for Module 1.

Every lab in Module 1 works in one repository, `global-bank-account`. It is a Spring Boot service
that records double-entry postings for client money. You clone it once, and each lab starts on its
own branch.

## How a lab step looks

Each step gives you a prompt to copy into **Copilot Chat**. The line above the prompt says how to
run it:

> **Prompt 1-A** · Agent mode · base model · **new chat**

- **Agent mode:** set the mode to **Agent** in the Copilot Chat box. Some steps say **Ask** or
  **Plan** instead. Those three are the modes you use here. If your version also lists Edit, ignore it.
- **Base model:** the default, lowest-cost model in your model list. Model names change often, so
  your trainer confirms which one to use on the day. Use the same model for every run in a lab, or
  the runs do not compare.
- **New chat:** start a new chat first, with the **+** at the top of the Chat view. **Same chat**
  means stay where you are.

Copy each prompt **exactly**. Everyone runs the same words, so the results compare fairly.

When Copilot asks to run a command or use a tool, **read the request before you select Allow**.

## One-time setup

### 1. Tools

- VS Code with **GitHub Copilot Chat**, signed in
- Git
- **JDK 25** and **Maven 3.9** or newer. Check with `java -version` and `mvn -version`
- **Python 3.14** (Lab 2 uses `python -m json.tool`). Some machines call it `python`, others
  `python3` — use whichever prints 3.14 from `python --version` or `python3 --version`
- **A bash shell.** The lab commands use bash. On Windows use **Git Bash** (it comes with Git for
  Windows) or WSL. On macOS or Linux any terminal will do

`./mvnw` does not work in this repository. Use `mvn`.

### 2. Clone this course

The lab tools, bundles and Module 4's agent live in this course repository. Clone it into your home
folder, because the lab commands expect it at `~/agentic-ai-copilot`:

```bash
cd ~
git clone https://github.com/ghewaredevopsai/agentic-ai-copilot.git
ls ~/agentic-ai-copilot/labs
# must include: module-2-tokens, module-3-python, module-4-agent, tickets
```

### 3. Clone the practice repository

```bash
mkdir -p ~/gb-labs && cd ~/gb-labs
git clone https://github.com/brainupgrade-in/global-bank-account.git
cd global-bank-account
git fetch --tags --force
```

Always add `--force`. Without it, git keeps any older copy of a tag that your clone already has.

Check that the tags arrived:

```bash
git tag --list 'm[134]-start*'
# must list: m1-start, m3-start, m4-start, m4-start-gh
```

**Nothing is pushed.** You work on local branches in your own clone, all day.

### 4. Build it once

```bash
git switch -c setup-check m3-start && mvn test
# expect: Tests run: 4, Failures: 0, Errors: 0
```

The first build downloads Maven packages, so it takes a few minutes. Do this before the session, not
during it.

### 5. Open both folders in one VS Code window

Open `global-bank-account`, then **File**, **Add Folder to Workspace**, and add this course folder,
`~/agentic-ai-copilot`.
Copilot then sees the code and the lab tickets at the same time. Every lab depends on this.

## Where each lab starts

The repository has **checkpoint tags**. Each one holds the code as a lab expects it.

| Tag | What the repository holds at that tag |
|---|---|
| `m1-start` | The posting service and its tests. Nothing the team knows is written down |
| `m3-start` | Adds the written knowledge: `.github/copilot-instructions.md`, `docs/architecture.md`, `docs/conventions.md`, `docs/glossary.md` and `docs/adr/` |
| `m4-start` | Adds the team's `account-change` skill file and `gb-change` prompt file |
| `m4-start-gh` | The same, with the `gb-change` prompt file reading its ticket from a GitHub issue. Lab 4 uses this one |

Each lab tells you which tag to branch from:

| Lab | Branch | From |
|---|---|---|
| 1 · Prompt teardown | `lab-1-teardown` | `m3-start` |
| 2 · Output contract | `lab-2-contract` | `m3-start` |
| 3 · Your instruction file | `lab-3-instructions` | `m1-start` |
| 4 · The A/B | `eval-A`, `eval-B` | `m3-start` |

Lab 3 starts from `m1-start` on purpose. You write the instruction file yourself, so you need a
repository that does not have one yet.

## Tickets

The lab tickets are Markdown files in [`tickets/`](tickets/). You read them in chat with `#file:`.
Type `#file:GB-151.md` and pick `labs/tickets/GB-151.md` from the list. Copilot then has the whole
ticket.

Seven tickets are here. The labs use GB-151, GB-204, GB-205 and GB-206. GB-201, GB-202 and GB-203
are spares for the stretch lab.

**If you would rather use GitHub issues,** copy a ticket's text into an issue in your own repository
and read it with the GitHub MCP server instead. Nothing in the labs depends on this. One warning if
you do: the team's `gb-change.prompt.md` (Lab 4) already reads a GitHub issue, and Lab 4 tells you to
replace that line with the Markdown file. Keep the GitHub issue line instead, and point it at your own
issue.

## Your notes

Each lab writes notes to `labs/my-work/` in this course folder. That folder is yours. It is not
committed, and nobody reads it but you.

```bash
mkdir -p ~/agentic-ai-copilot/labs/my-work
```

Use the full path. If you run it from inside `global-bank-account`, the folder lands in the
practice repository, and every "must print nothing" check in the labs then fails.

## Running a lab again

`git switch -c` fails if the branch is already there from an earlier attempt. Delete it first, from
another branch:

```bash
git switch --detach m3-start
git branch -D lab-1-teardown        # the branch you are about to make again
```

To keep the earlier attempt, rename it instead: `git branch -m lab-1-teardown first-attempt-1`.

## If Copilot goes wrong

- **It edits the wrong thing:** select **Undo** on the change in the chat, or run `git restore .` in
  the repository.
- **It gets stuck:** select **Stop**, start a new chat and paste the step's prompt again.
- **It asks to run a command you do not understand:** select **Skip**, and ask your trainer.
- **A lab leaves files behind:** every lab ends with a reset. Run `git status --short`. If it prints
  anything, run `git stash push -u -m "leftovers"` and carry on.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
