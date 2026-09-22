# Solutions

Every mission is solved with **GitHub Copilot, not by hand**. So a solution here is mostly a sequence of Copilot
prompts, with what to check after each one. The finished code is also here, for comparing and catching up.

| Mission | Prompts | Code |
|---|---|---|
| 1 &mdash; Python drills | [`mission-1.md`](mission-1.md) | [`code/mission-1/`](code/mission-1/) &mdash; `katas/drills.py` |
| 2 &mdash; Core package | [`mission-2.md`](mission-2.md) | [`code/mission-2/`](code/mission-2/) &mdash; `askops/errors.py`, `store.py`, `search.py` |
| 3 &mdash; JSON API | [`mission-3.md`](mission-3.md) | [`code/mission-3/`](code/mission-3/) &mdash; `askops/schemas.py`, `api.py` |
| 4 &mdash; Web page | [`mission-4.md`](mission-4.md) | [`code/mission-4/`](code/mission-4/) &mdash; `askops/web.py`, `askops/templates/` |
| 5 &mdash; Review and ship | [`mission-5.md`](mission-5.md) | [`code/mission-5/`](code/mission-5/) &mdash; `askops/api.py` with the failure contract |

## When to use them

- **Solve the mission with Copilot first**, using the lab. The prompts here are one route that works, not the only
  one, and a solution read beforehand teaches far less than one you compare against afterwards.
- **Stuck on a prompt?** Compare yours with the mission file. The difference is usually the context you gave the
  agent (the spec, the tests, "do not modify tests"), not the wording.
- **Copilot's output varies.** The same prompt gives different code on different runs. The tests decide what is
  correct, so the code you get does not have to match `code/`.
- **Fell behind?** Switch to a checkpoint tag and start the next mission green (below).

## Compare with yours

From your AskOps clone, diff your file against the tag that has the mission solved (`mission-3-start` has
mission 2 solved):

```bash
git diff mission-3-start -- askops/store.py
```

Where they differ, decide which one you would rather maintain.

## Catch up to a mission

The code stacks: to start mission 4 green you need missions 1 to 3. Your AskOps clone has a **checkpoint tag**
for each mission, `mission-N-start`, with every mission before N solved. Commit your own work first, then switch:

```bash
cd ~/askops
git add -A && git commit -m "my work so far"
git switch -c catch-up mission-4-start       # missions 1-3 solved
python score.py                              # 47/56
```

Expected scoreboard at `mission-2-start` to `mission-5-start`, then `mission-5-done`: **20, 34, 47, 54, 56** of 56.
The tags hold the same code as `code/` here.

## Mission 5

Open `mission-5.md` and `code/mission-5/` only after you have reviewed PR #42 yourself and run the scoreboard on
it (Lab 5, steps 1 and 2). They show the fix, and that gives the review away.
