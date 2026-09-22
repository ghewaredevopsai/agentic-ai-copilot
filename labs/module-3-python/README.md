# Module 3 — Python Accelerated with Copilot: six labs, one app

Hands-on labs for Module 3. Every lab builds the same application,
**AskOps**, from a pile of failing tests to a running web app, in about
two and a half hours of hands-on time.

## How these labs work

- **The tests are the spec.** Each mission ships with failing tests. Nobody tells you to "write a
  function that...". You run `python score.py N`, read what is red, and make it green. That is how you
  will work with an AI agent at your desk too.
- **Copilot writes the code. You never implement by hand.** What you practise is everything around it:
  predicting, directing, reading, explaining and deciding.
  - **Tutor** (Lab 1): `/tutor` explains the Python idea against the language you already know, writes the
    code, runs the tests and asks you a question you must answer. You are building the reading skill every
    later lab depends on.
  - **Builder** (Labs 2 to 5): agent mode, driven from a spec or a TODO, with the tests as the finish line.
    You direct; it types; you review every diff.
- **Read before you run.** Every lab has a *read first* step. Reviewing Python you did not write is the
  skill this module is really about.
- **Nobody falls behind.** Behind at the start of a lab? Switch to its checkpoint tag
  ([Stuck?](#stuck)) and start the next mission green. Solve it with Copilot first, then compare.
- **Copilot's output varies.** Two people running the same prompt get different code. The tests decide
  what is correct, not the transcript you are shown.

## The labs

| Lab | Tier | Time | Mission | You leave with |
|---|---|---|---|---|
| [0 &mdash; Set up and meet your tutor](lab-0-set-up-and-meet-your-tutor.md) | T0 | 5 min | &mdash; | A venv, a red scoreboard and a working `/tutor` |
| [1 &mdash; Drills with a tutor](lab-1-drills-with-a-tutor.md) | T1 | 30 min | 1 | Collections, comprehensions, errors, dataclasses in your fingers |
| [2 &mdash; Build the core package](lab-2-build-the-core-package.md) | T2 | 25 min | 2 | A package with errors, logging and search, tested |
| [3 &mdash; The API, spec-first](lab-3-the-api-spec-first.md) | T3 | 35 min | 3 | A FastAPI service with pydantic contracts and concurrent async I/O |
| [4 &mdash; Put a web page on it](lab-4-put-a-web-page-on-it.md) | T4 | 20 min | 4 | A web app that updates without page reloads |
| [5 &mdash; Review, reject, ship](lab-5-review-reject-ship.md) | T5 | 15 min | 5 | A rejected PR, a failure contract, and a PR of your own |

## Set up

**You need:** Python 3.12 or newer (3.14 recommended), git, VS Code with GitHub Copilot signed in (a seat
that includes agent mode), and access to PyPI for `pip install`. A GitHub account for Lab 5's pull
request is useful but not required.

Clone AskOps, install it, and open **the clone** as the workspace:

```bash
git clone https://github.com/ghewaredevopsai/askops.git ~/askops
cd ~/askops
python -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
code .
```

Copilot reads `.github/copilot-instructions.md` and `.github/prompts/` from the workspace root. The tutor
and the house rules only work when the AskOps clone is the folder you open. Keep this course folder in a
separate VS Code window for the lab guides.

Work in your clone, and do not push to it. For Lab 5's pull request, push to a repository of your own.

Then start [Lab 0](lab-0-set-up-and-meet-your-tutor.md).

## Stuck?

Paste the failing check into Copilot Chat. Ask it to explain the cause before it fixes anything.

Still stuck, or behind? Every mission has a **checkpoint tag**. `mission-N-start` has every mission
before N solved, so you start mission N green. Commit your own work first, then switch:

```bash
git add -A && git commit -m "my work so far"
git switch -c catch-up mission-4-start       # missions 1-3 solved, ready for mission 4
python score.py                              # 47/56
```

| Tag | Solved | Score |
|---|---|---|
| `mission-1-start` | nothing (the starter) | 1/56 |
| `mission-2-start` | 1 | 20/56 |
| `mission-3-start` | 1&ndash;2 | 34/56 |
| `mission-4-start` | 1&ndash;3 | 47/56 |
| `mission-5-start` | 1&ndash;4 | 54/56 |
| `mission-5-done` | all | 56/56 |

To see how a mission was solved: `git diff mission-3-start mission-4-start`. The Copilot prompts behind each
solution are in [`solutions/`](solutions/README.md). Solve each mission with Copilot first: a solution teaches
most when you compare it with what your agent produced.

## What each lab covers

[`learning-outcomes.md`](learning-outcomes.md) lists what you can do at the end of the module, and which lab
checks it.
