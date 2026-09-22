# Lab 2 &mdash; Build the core package

**Tier 2 &middot; Structure** &nbsp;|&nbsp; ~25 minutes &nbsp;|&nbsp; Mission 2 &nbsp;|&nbsp; Copilot: **your choice**

## The situation

AskOps needs a core that knows nothing about HTTP: domain errors, a store that loads JSON without falling
over on one bad record, and a keyword search. It is the part every later mission, and the agent brain you
add later in the course, is built on.

## Read first (5 minutes, no editing)

Open these and read them top to bottom. Ask Copilot Chat about anything you would not approve in a review.

- `askops/models.py` &mdash; `@dataclass(frozen=True, slots=True)`, `StrEnum`, a `classmethod` constructor
- `askops/store.py` &mdash; what is done, and the four TODOs
- `askops/search.py` &mdash; the docstring *is* the spec
- `tests/test_m2_core.py` &mdash; especially `caplog` and `tmp_path`, two pytest fixtures you get for free

Answer for yourself: **which module imports which?** Draw it. If `store` ever imports `search`, you have
a cycle.

## Do

Copilot writes the code; you steer and review. Commit first (`git add -A && git commit -m "before mission 2"`) so
every change is visible in `git diff`. Then work through the three files in order, in **Agent** mode, a new chat
each time:

1. **Errors.**

   ```text
   Complete the TODO in askops/errors.py. Run python score.py 2 and report which checks still fail.
   ```

   Review: both classes subclass `AskOpsError`? `RunbookNotFound` keeps `.runbook_id`?

2. **Store.**

   ```text
   Complete the TODOs in askops/store.py, one at a time. Do not change tests or other files.
   Run python score.py 2 after each TODO.
   ```

   Review in `git diff`: one bad incident record is skipped **with a WARNING naming its id**, not the whole file;
   `raise ... from` is used deliberately; logging uses `%s` arguments, not f-strings.

3. **Search.**

   ```text
   Implement search() in askops/search.py exactly as its docstring specifies. Use set operations for scoring.
   Run python score.py 2.
   ```

   Review: can you explain the scoring line out loud? Does it iterate `store.runbooks()`?

If a check stays red, paste the failure into the same chat and ask the agent to explain the cause **before**
it fixes it.

## Notice

- **`raise RunbookNotFound(runbook_id) from None`** hides the `KeyError` from the traceback; `from exc`
  keeps it as the cause. Pick deliberately: would the person on call want to see the original?
- **`logger.warning("skipping incident %s: %s", id, exc)`** passes arguments instead of an f-string.
  The message is only formatted if that level is enabled, and log aggregators can group by the template.
  Copilot will often suggest the f-string. It works. It is still the wrong habit.
- **Sets do the scoring.** `words & title_words` is set intersection. If your search loops over words
  and counts, it passes; compare it with the set version and decide which you would rather review.
- **Returning `sorted(...)`** gives callers a new list, which is why `test_incidents_returns_a_copy` passes
  without an explicit copy.

## Done when

`python score.py 2` shows **Score: 14/14**, and `python score.py 1` is still 19/19. Commit.

## Stretch

Ask Copilot for a `@timed` decorator in `askops/timing.py` that logs how long a function took at `DEBUG`, applied
to `search`. Then explain every line of it back to yourself, especially `functools.wraps` and `*args, **kwargs`.
It is the pattern behind half the framework decorators you are about to use: `@router.get`, `@pytest.fixture`,
`@tool`.
