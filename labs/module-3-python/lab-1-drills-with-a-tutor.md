# Lab 1 &mdash; Drills with a tutor

**Tier 1 &middot; Data** &nbsp;|&nbsp; ~30 minutes &nbsp;|&nbsp; Mission 1 &nbsp;|&nbsp; Copilot: **`/tutor`**

## The situation

Before you let an agent build a Python service for you, you need to read Python fast enough to catch it
when it is wrong. Fifteen drills, each a real task you meet in every service: counting, grouping, parsing,
value objects, reading a file. Copilot writes every one. Each drill also has a Python-specific way to go
wrong, and you have to spot it.

## The loop, for every drill

1. **Predict.** Read the drill's docstring and its test in `tests/test_m1_drills.py`. Say in one line how *you*
   would write it in your own language.
2. **Generate.** In Copilot Chat: `/tutor` and the drill's name, for example `word_counts`. It explains, writes
   the function, and runs `python score.py 1`.
3. **Explain it back.** Answer the tutor's check question. If you cannot, ask it to explain again another way.
   Do not move on until you can.
4. **Compare.** How far was the Python from your prediction? That gap is what you just learned.

Batch drills when they are easy for you (`/tutor word_counts, unique_services and high_severity_titles`), and
slow down on the ones marked below.

## Do

1. **Collections (5 drills).** `word_counts` to `group_by_service`. Two must be *one* comprehension; check that
   Copilot's version is, and that you could read it aloud.
2. **Functions and truthiness (3 drills).** Slow down here. `first_or_default` must work on a generator, which
   has no index and no length. `add_tag` is the most famous bug in Python. Before generating it, predict what
   `tags=[]` would do on the second call.
3. **Errors (2 drills).** `parse_port` raises; `port_or_default` must *reuse* it. Ask the tutor what *EAFP* means.
4. **Dataclasses (2 drills).** `Money` is frozen; `Ticket` has two bugs in its field declarations. Before you run
   `/tutor Ticket`, find both bugs yourself by reading `askops/models.py`.
5. **Files (1 drill).** `read_nonblank_lines`, with `with`.

## Notice

- **`tags=[]` as a default is created once**, when the function is defined, and then shared by every call. The
  same trap is `watchers: list = None` in a dataclass. In Java or C# the equivalent would be a static field that
  nobody writes by accident. In Python everyone writes it once, and Copilot suggests it more often than you think.
- **Truthiness:** `user.get("name") or user.get("email") or "anonymous"` is idiomatic, and it treats `""`, `0`,
  `[]` and `None` alike. That is exactly right here, and exactly the bug when `0` is a valid value.
- **Type hints are not checked at runtime.** `Money("10", 5)` constructs happily. Hints are for readers, your
  editor and tools like mypy, not for the interpreter.

## Done when

`python score.py 1` shows **Score: 19/19**, and you answered every check question. Commit:

```bash
git add -A && git commit -m "Mission 1: drills"
```

## Stretch

In Chat (not `/tutor`): *"Review katas/drills.py as a strict senior Python reviewer. What is not idiomatic, and
what would break on unusual input?"* Decide which findings you agree with, and have Copilot apply only those.
