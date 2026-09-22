# Module 3 &mdash; Python Accelerated with Copilot: learning outcomes

What you will be able to do at the end of the module, how the module checks it, and why each outcome is here.

## Outcomes

| # | You can... | Evidence in the module |
|---|---|---|
| 1 | **Read idiomatic Python** at working speed: comprehensions, unpacking, truthiness, dataclasses, decorators, `with` | Lab 1 drills (19 checks); tiers 0&ndash;2 "Read the PR" votes |
| 2 | **Spot the Python-specific bugs** that experienced engineers from other languages write once: mutable defaults, `is` for values, truthiness hiding zero, unenforced type hints | Lab 1 checks `add_tag`, `display_name`, `Ticket`; tier 0/1 PR slides |
| 3 | **Structure a small package** with a domain exception hierarchy, per-module logging, and errors translated at the edge | Lab 2 (14 checks) |
| 4 | **Build a typed JSON API** with FastAPI and pydantic v2, including validation, 404/422 semantics and dependency injection | Lab 3 (11 checks), `/docs` used by hand |
| 5 | **Use async correctly**: concurrent awaits with `gather`, and never blocking I/O inside `async def` | Lab 3 timing check; tier 3 PR slide |
| 6 | **Build a server-rendered web page** on the same app, with htmx, safe templating and one shared validation contract | Lab 4 (8 checks, including XSS escaping); used in a browser |
| 7 | **Test a Python service** with pytest fixtures, `TestClient` and dependency overrides | Read and run the 56 checks; the Lab 3 and Lab 5 stretch goals write new ones |
| 8 | **Direct Copilot deliberately**: a tutor that explains before it writes, spec-first agent mode to build, tests as the finish line &mdash; with no code written by hand | Labs 1&ndash;5 |
| 9 | **Review and reject AI-written Python** that passes tests, and say which findings no test caught | Lab 5: review PR #42, then prove it wrong with the tests |
| 10 | **Ship with git hygiene**: a branch per concern, checkpoint commits around agent work, messages that say why | Lab 5 |

## Why these outcomes

- **Scope.** The Python that an engineer on an AI-assisted team needs in practice: the language itself (types,
  packages, dataclasses, exceptions, logging), type hints and pydantic, a FastAPI service with async I/O, tests
  as the guardrail, reviewing and rejecting AI-written code, and Git hygiene &mdash; with GitHub Copilot used as a
  tutor and as a builder throughout.
- **Audience.** Written for engineers who already program professionally in another language. Nothing is taught
  that you can guess from Java, C#, TypeScript or Go; the time goes to where Python is different, and to building
  a real application before the session ends.
- **Tests as the spec.** Every lab is checked by the same pytest suite, reported as `[PASS]`/`[FAIL]` lines and
  a score. It is how you will know you are done, and it is how you will direct an agent at work.
- **Versions.** Checked on Python 3.14.4 with FastAPI 0.141.1, Starlette 1.6.0, pydantic 2.13.5, uvicorn 0.53.0,
  Jinja2 3.1.6, pytest 9.1.1, httpx 0.28.1, python-multipart 0.0.32, and htmx 2.0.10 (included in the repository).
