# Mission 2 &mdash; the core package, solved with Copilot

**Lab:** [Lab 2 &mdash; Build the core package](../lab-2-build-the-core-package.md) &nbsp;|&nbsp; **Checks:** 14
&nbsp;|&nbsp; **Copilot:** Agent mode &nbsp;|&nbsp; **Code:** [`code/mission-2/`](code/mission-2/)

## Before you start

- Mission 1 is green, or you are on the `mission-2-start` tag.
- `git add -A && git commit -m "before mission 2"`
- Copilot Chat in **Agent** mode. Start a **new chat** for each step, so each prompt carries only its own context.

## 1. Read before you build

Ask mode:

```text
Explain askops/models.py to an engineer who knows Java: what @dataclass(frozen=True, slots=True), StrEnum and
the from_dict classmethod each do, and which of them a Java record has no equivalent for. Then draw the import
graph of the askops package as text.
```

**Check:** you can say why `store` may import `models` but must never import `api`.

## 2. The exception hierarchy

```text
Complete the TODO in askops/errors.py. Keep it minimal: RunbookNotFound(runbook_id) with a .runbook_id
attribute and a message that includes the id, and DataError. Both subclass AskOpsError.
Run python score.py 2 and tell me which checks still fail and why.
```

**Check:** `RunbookNotFound.__init__` calls `super().__init__(f"runbook {runbook_id} not found")`. No other file
changed (`git diff --stat`).

## 3. The store

```text
Complete the four TODOs in askops/store.py, one at a time, following the comment on each and
tests/test_m2_core.py. Do not modify tests or any other file.
- Load incidents.json. A record that fails to parse is skipped with logger.warning naming its id.
- _read_json turns FileNotFoundError and json.JSONDecodeError into DataError, with the path in the message.
- get_runbook uses try/except KeyError (EAFP) and raises RunbookNotFound from None.
- add_incident validates runbook_id first, then assigns the next INC- number.
Run python score.py 2 after each TODO.
```

**Check, in `git diff askops/store.py`:**
- the `try/except` is **inside** the loop over incident records, not around it
- the exceptions caught are `KeyError, ValueError, TypeError` &mdash; not `Exception`
- logging uses `%s` arguments, not f-strings
- `incidents()` returns `sorted(...)`, a new list, newest first

## 4. Search

```text
Implement search() in askops/search.py exactly as its docstring specifies. Use set intersection for the
title-word and tag scoring. Log the DEBUG line from the docstring with %-style arguments.
Run python score.py 2.
```

**Check:** the score is `len(words & title_words) + 2 * len(words & rb.tags)`; hits sort by
`(-score, runbook_id)`; a query with no word of 3+ characters raises `ValueError`.

## 5. Explain it back

Ask mode:

```text
In askops/store.py, what is the difference between "raise RunbookNotFound(id) from None" and "from exc"?
Which traceback would the on-call engineer see in each case?
```

## Done

```bash
python score.py 2        # Score: 14/14
python score.py 1        # still 19/19
git add -A && git commit -m "Mission 2: core package with domain errors, logging and search"
```

## If a check stays red

```text
<paste the [FAIL] line>. Explain the cause first. Then fix it without modifying tests, and run python score.py 2.
```
