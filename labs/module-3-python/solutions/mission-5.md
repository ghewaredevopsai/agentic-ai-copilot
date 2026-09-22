# Mission 5 &mdash; review, reject, ship, solved with Copilot

**Lab:** [Lab 5 &mdash; Review, reject, ship](../lab-5-review-reject-ship.md) &nbsp;|&nbsp; **Checks:** 4 &nbsp;|&nbsp;
**Copilot:** Ask mode as a second reviewer, then Agent mode &nbsp;|&nbsp; **Code:** [`code/mission-5/`](code/mission-5/)

> **Spoiler.** This file discusses what is wrong with PR #42. Do Lab 5 steps 1 and 2 first: review the PR on paper,
> then apply it and run the scoreboard.

## Before you start

- Missions 1 to 4 are green (`python score.py` shows **54/56**), or you are on the `mission-5-start` tag.
- `git add -A && git commit -m "before mission 5"`

## 1. Apply the PR, as the engineer who clicked Merge

```bash
git switch -c pr-42
cp -r review/pr-42/. .          # the PR's api.py and search.py, over yours
python score.py
```

`git apply review/pr-42-ask-resilience.diff` will **not** work: the diff was made against the PR author's code, and
yours was written by your agent. The `.diff` is for reading in the review; `review/pr-42/` is for running.

**Check:** the score drops from 54 to 51. Five checks are red, and the PR caused three of them:
`test_search_respects_limit`, `test_ask_consults_both_sources_concurrently` and
`test_a_bug_is_not_disguised_as_unavailable`. The other two are Mission 5 checks that were already red before
the PR, because the failure contract is not written yet.

## 2. A second reviewer, after your own review

Ask mode, **after** you have written your own findings:

```text
Review review/pr-42-ask-resilience.diff as a strict senior Python reviewer, against docs/api-spec.md and
.github/copilot-instructions.md. For each problem: the line, why it is wrong, which test in tests/ catches it
(or "no test catches this"), and the fix. Do not edit files.
```

**The four problems:**

| Problem | Caught by |
|---|---|
| The two sources are awaited one after the other, so `/ask` takes ~0.4 s | `test_ask_consults_both_sources_concurrently` |
| `except Exception` returns an empty 200 when a source fails | `test_a_bug_is_not_disguised_as_unavailable` |
| `_cache: dict = {}` is a mutable default argument, shared across calls and stores, keyed on query but not `limit` | `test_search_respects_limit` |
| `le=20` removed, so `limit` is unbounded | **no test** &mdash; only review catches it |

Compare the table with your own findings. If Copilot missed one that you found, or found one you missed, that is
the lesson of the lab.

## 3. Reject it

```text
Write review/my-review.md: a pull request review that blocks PR #42. Use my findings: <paste yours>.
For each, cite the test that proves it or say no test catches it, and state the fix. Keep it under 200 words.
```

**Check:** the findings are yours; Copilot only tightened the wording. Then throw the PR away. The PR's changes
were never committed, so undo them **before** switching, or they follow you back onto your own branch:

```bash
git restore askops tests          # drop PR #42's changes; your untracked review file stays
git switch - && git branch -D pr-42    # back to the branch you were on
git status                        # only review/my-review.md is new
```

## 4. Do it properly

```text
Implement the "Mission 5 - the failure contract" section of docs/api-spec.md in askops/api.py only.
Catch AskOpsError only, log it with logger.exception, and raise HTTPException 503 with detail
"search unavailable". Anything that is not an AskOpsError must propagate. Do not modify tests.
Finish by running python score.py.
```

**Check, in `git diff askops/api.py`:** `except AskOpsError`, not `except Exception`; `logger.exception(...)`;
`status.HTTP_503_SERVICE_UNAVAILABLE`; `raise ... from exc`. `python score.py` shows **56/56**.

## 5. Ship it

```bash
git switch -c fix/ask-failure-contract
git add askops/api.py review/my-review.md
```

```text
Write a commit message for the staged changes: a subject under 72 characters that says why, and a short body.
```

```bash
git commit          # paste the message, edit it until you agree with every word
```

With a GitHub account: create a private repository, `git remote add mine <url>`, `git push -u mine HEAD`, open
a pull request, and request a review from Copilot.

## Done

`python score.py` shows **Score: 56/56**, and your branch has a commit whose message explains the why.

## Stretch &mdash; close the gap the tests left

```text
Add a test to tests/test_m3_api.py: GET /api/ask with limit=21 must return 422. Only the test, no other change.
Run pytest tests/test_m3_api.py.
```

It passes on your code. Optional: `git stash`, apply PR #42 again on a branch, and watch it fail there. The
scoreboard then shows 57/57, the 56 checks plus your test.
