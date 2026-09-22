# Mission 1 &mdash; Python drills, solved with Copilot

**Lab:** [Lab 1 &mdash; Drills with a tutor](../lab-1-drills-with-a-tutor.md) &nbsp;|&nbsp; **Checks:** 19 &nbsp;|&nbsp;
**Copilot:** the `/tutor` prompt file &nbsp;|&nbsp; **Code:** [`code/mission-1/`](code/mission-1/)

## Before you start

- Your `askops` clone is open in VS Code as the workspace root, the venv is active, and `python score.py 1` runs.
- `/tutor` appears when you type `/` in Copilot Chat. If not, you opened the wrong folder.
- Commit, so you can see each drill's change: `git add -A && git commit -m "before mission 1"`.

For every drill: **predict** in one line how you would write it in your language, **run** the prompt, **answer**
the tutor's check question, and **read** the diff before the next drill.

## 1. Collections

```text
/tutor word_counts. I know Java best.
```

```text
/tutor unique_services and high_severity_titles
```

```text
/tutor index_by_id and group_by_service
```

**Check:** `high_severity_titles` and `index_by_id` are each **one** comprehension. `word_counts` uses
`Counter` or a dict comprehension, not a manual loop with `if key in d`. `group_by_service` uses `defaultdict(list)`
or `setdefault`. Score so far: **5/19**.

## 2. Functions and truthiness

Predict first: what does `def add_tag(tag, tags=[])` return on the *second* call?

```text
/tutor first_or_default. It must work on generators, so explain why len() and [0] are not options.
```

```text
/tutor add_tag. Before writing it, show me what would go wrong with tags=[] on two calls.
```

```text
/tutor display_name
```

**Check:** `first_or_default` uses `next(iter(items), default)`. `add_tag` creates a new list when
`tags is None`, and never uses `[]` as a default. `display_name` is a single `or` chain. Score: **8/19** (the
parametrised `parse_port` checks count separately).

## 3. Errors

```text
/tutor parse_port. Explain EAFP compared with checking the string first.
```

```text
/tutor port_or_default. It must reuse parse_port.
```

**Check:** `parse_port` wraps `int(value)` in `try/except ValueError` and raises `ValueError("invalid port: ...")`
for both non-numbers and out-of-range values. `port_or_default` calls `parse_port` inside a `try`. Score: **16/19**.

## 4. Dataclasses

Before prompting, open `askops/models.py` and find the two bugs in `Ticket`'s fields yourself.

```text
/tutor Money.add. Explain what frozen=True gives me compared with a Java record.
```

```text
/tutor Ticket. I think the bugs are: <your two findings>. Tell me if I am right before you fix it.
```

**Check:** `Money.add` returns a **new** `Money` and raises `ValueError` on a currency mismatch. `Ticket.watchers`
uses `field(default_factory=list)`, and `__post_init__` raises `ValueError` outside 1..4. Score: **18/19**.

## 5. Files

```text
/tutor read_nonblank_lines
```

**Check:** it uses `with open(...)`, strips each line, and skips blank lines and `#` comments. It accepts a `str`
or a `Path`.

## Done

```bash
python score.py 1        # Score: 19/19
git add -A && git commit -m "Mission 1: drills"
```

## If a drill stays red

```text
tests/test_m1_drills.py::<test name> fails with: <paste the [FAIL] line>.
Explain the cause first, in two sentences, then fix only that function and run python score.py 1.
```
