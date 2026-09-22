# Video Resources — Python Accelerated (Day 1, Block 1.3)

Pre-/post-session viewing for block **1.3 Python Accelerated with Copilot — the AskOps API**. The
outline covers: the Python you need (types, packages, dataclasses, exceptions, logging) · type hints
and pydantic · Copilot as tutor · spec-first vibe coding in agent mode · FastAPI service, async & I/O ·
tests as the guardrail · AI code review, when to reject · Git hygiene.

All ten are between 1 and 2 hours. Length, publish date, channel and playability were read from each
video page on **17 Sep 2026**; the videos have not been watched end to end, so preview before showing
one in a session. Ordered as a learning path: Python core → typed/async/API Python → tests → AI-assisted
development → Git.

All ten are collected, in this order, in the public YouTube playlist
[python-accelerated](https://www.youtube.com/playlist?list=PLQq5Us5Jlqs8) on the Gheware DevOps AI
channel (`@GhewareDevOpsAI`), created 17 Sep 2026 and verified from an anonymous fetch. Check it with
`curl -s "https://www.youtube.com/playlist?list=PLQq5Us5Jlqs8" | grep -oE '"videoId":"[A-Za-z0-9_-]{11}"'`.

## Python core (beginner → intermediate)

| # | Video | Channel | Published | Length | Covers (block 1.3 point) |
|---|-------|---------|-----------|--------|--------------------------|
| 1 | [Python As Fast as Possible - Learn Python in ~75 Minutes](https://www.youtube.com/watch?v=VchuKL44s6E) | Tech With Tim | Oct 2020 | 1:19:41 | Whole language at speed: types, collections, functions, exceptions, modules. |
| 2 | [Python Crash Course For Beginners](https://www.youtube.com/watch?v=JJmcL1N2KQs) | Traversy Media | Nov 2018 | 1:35:47 | Variables, data structures, functions, classes, modules/packages, files. |

## Typed, async and API Python (intermediate → advanced)

| # | Video | Channel | Published | Length | Covers |
|---|-------|---------|-----------|--------|--------|
| 3 | [Python Pydantic Tutorial: Complete Data Validation Course (Used by FastAPI)](https://www.youtube.com/watch?v=M81pfi64eeM) | Corey Schafer | Oct 2025 | 1:29:25 | Type hints and pydantic models/validation. |
| 4 | [Python Tutorial: AsyncIO - Complete Guide to Asynchronous Programming with Animations](https://www.youtube.com/watch?v=oAkLSJNr5zY) | Corey Schafer | Aug 2025 | 1:42:41 | async/await, coroutines, tasks, async I/O. |
| 5 | [FastAPI Crash Course - Modern Python API Development](https://www.youtube.com/watch?v=8TMQcRcBnW8) | Traversy Media | Jan 2026 | 1:00:21 | FastAPI service — the AskOps API shape. |
| 6 | [Pytest Tutorial – How to Test Python Code](https://www.youtube.com/watch?v=cHYq1MRoyI0) | freeCodeCamp.org | Oct 2023 | 1:28:39 | Tests as the guardrail: pytest, fixtures, parametrize, mocking. |

## AI agents to accelerate learning and building

| # | Video | Channel | Published | Length | Covers |
|---|-------|---------|-----------|--------|--------|
| 7 | [Python Pulse - Learn Python with GitHub Copilot](https://www.youtube.com/watch?v=vM6HllvO6ww) | Visual Studio Code (official) | Feb 2024 | 1:03:45 | Copilot as tutor: a developer new to Python learns it live with Copilot. Older Copilot UI. |
| 8 | [How to use GitHub Copilot (the complete beginner's guide)](https://www.youtube.com/watch?v=SJqGYwRq0uc) | GitHub (official) | Jul 2025 | 1:33:24 | Chat, agent mode, security best practice, hands-on projects. |
| 9 | [AI-Assisted Coding Tutorial – OpenClaw, GitHub Copilot, Claude Code, CodeRabbit, Gemini CLI](https://www.youtube.com/watch?v=wlpBCazAY9Q) | freeCodeCamp.org | Mar 2026 | 1:25:26 | Agentic coding workflows plus AI code review (CodeRabbit) — when to accept or reject. |

## Git hygiene

| # | Video | Channel | Published | Length | Covers |
|---|-------|---------|-----------|--------|--------|
| 10 | [Git & GitHub Crash Course for Beginners [2026]](https://www.youtube.com/watch?v=mAFoROnOfHs) | freeCodeCamp.org | Dec 2025 | 1:21:20 | Branching, merging, stash, rebase, pull requests. |

## Gaps and considered-but-skipped

- **Dataclasses and logging** have no good 1–2 h video; they are only touched inside #1/#2. Shorter
  options if needed: Raymond Hettinger's PyCon 2018 dataclasses talk (45 min), Corey Schafer's type
  hints video (41 min).
- **Spec-first vibe coding** is shown only generally (#8, #9). Matt Pocock's *Workflow for AI Coding*
  (1:36) is strong but TypeScript; GitHub Spec Kit live streams were low-quality.
- Skipped as over 2 h or overlapping: Mosh / Apna College full courses (2:02), codebasics *Python for
  AI in 2 Hours* (2:02:53), Telusko FastAPI (2:02), freeCodeCamp 4–19 h courses. *Python unit testing
  with GitHub Copilot* (Tech with Brylie, 1:23, 2023 stream) was a close alternative to #7.
