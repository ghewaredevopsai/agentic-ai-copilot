# Module 2 — reference answers

Look whenever you want. These labs are measured, not scored, so there is nothing to give away.
Only Lab 1 is spoiled by reading ahead: write your predictions down first.

Every token figure below was measured on `global-bank-account` at tag `m3-start`, with the
`ctxmeter` in this folder. If the repository or `ctxmeter` changes, measure again.

---

## Lab 0 — Count your own bundle

| Measurement | Value |
|---|--:|
| `everything.txt` | 23,756 est. tokens |
| `naive.txt` | 18,261 est. tokens |
| Saved by leaving out the build scripts and the CI workflows | 5,495 (23.1%) |
| Turn 1 of `naive.txt` sends | 18,261 |
| Turn 10 sends | 22,761 |
| 10 turns in total | 205,110 est. input tokens, for 2,500 tokens of answers |

**Which files are the biggest?** `mvnw` (2,832), `AccountController.java` (2,307), `mvnw.cmd`
(1,770) and `pom.xml` (1,226). None of them decides how a posting works. Two are scripts that start
Maven.

**How much of `naive.txt` is the older account code?** About 8,300 tokens, **48%** of the attached
files. `docs/architecture.md` says that code is out of scope for posting work.

**The credit figure.** Any of the three outcomes is a correct answer. What matters is that you wrote
down which one you got.

**What `ctxmeter` can never see:** Copilot's hidden system prompt, Copilot's own search, files the
agent opens by itself, and the exact form of the tool definitions. So each number is a minimum.

## Lab 1 — One matrix row

Read this only after your predictions are written down.

| task | fast | default | reasoning |
|---|---|---|---|
| explain-code | kept 3/4 · 0.4 cr | kept 4/4 · 1.1 cr | kept 4/4 · 6.4 cr |
| write-docstring | kept 4/4 · 0.3 cr | kept 2/4 · 0.9 cr | kept 4/4 · 5.6 cr |
| mechanical-rename | kept 3/4 · 0.5 cr | kept 4/4 · 1.2 cr | kept 3/4 · 7.5 cr |
| write-unit-test | kept 0/4 · 0.7 cr | kept 3/4 · 1.6 cr | kept 3/4 · 8.5 cr |
| find-subtle-bug | kept 1/4 · 0.6 cr | kept 3/4 · 1.7 cr | kept 4/4 · 9.5 cr |
| multi-file-feature | kept 1/4 · 1.1 cr | kept 3/4 · 2.9 cr | kept 4/4 · 11.9 cr |

**This data is made up, and the file says so.** Think about the patterns. Replace the file with your
own runs before you quote a row.

- **The fast model is fine for explaining, documenting and renaming.** It keeps 3 or 4 of 4, at about
  a fifteenth of the reasoning model's cost. Most teams do most of their work here.
- **The fast model fails on tests:** 0 of 4 kept. Cheap and useless is not cheap.
- **`write-unit-test` is the clearest value row.** Default keeps 3 of 4 at 1.6 credits. Reasoning
  keeps 3 of 4 at 8.5. Five times the price for no gain.
- **The reasoning model loses on `mechanical-rename`:** 3 of 4 against default's 4 of 4, at six times
  the cost.
- **`write-docstring` default at 2 of 4 is noise.** Four runs cannot separate it from the others on a
  task all three can do.

A row you could defend:

```markdown
For unit tests we use the default model type, because in our runs
it kept 3 of 4 results at about a fifth of the reasoning model's
cost, and the reasoning model also kept 3 of 4. Multi-file changes
are different: there reasoning kept 4 of 4, so we use it and read
the change.
We check this again when the model list changes, or when fewer than
3 in 4 of our test results are kept for two weeks.
```

It names the tasks, it quotes a number instead of a reputation, and it has a date to check it again.
Compare it with what people usually write: *"Use the reasoning model for anything important."* To the
person doing it, every task is important.

## Lab 2 — The cascade

```
gate < 0.40        70%       80          0%
gate < 0.50        75%      128          5%
gate < 0.60       100%      368         30%   cheapest at full accuracy
gate < 0.65       100%      368         30%   same cost - the plateau
gate < 0.70       100%      368         30%   same cost - the plateau
gate < 0.80       100%      560         50%   full accuracy, 1.5x the cost of 0.60
gate < 0.90       100%      800         75%   full accuracy, 2.2x the cost of 0.60
gate < 1.01       100%     1040        100%   costs MORE than always-strong
```

- **0.60 is the answer:** the strong model's accuracy for 38% of its price, a 62% saving.
- **0.60 to 0.70 is flat.** Pick the middle of it, so small changes in the data do not break it.
- **1.01 is the row to write down:** 1040 against always-strong's 960, with 100% accuracy.
- **0.80 and 0.90 are waste that looks careful:** still 100%, at 1.5 and 2.2 times the cost of 0.60.
- **Confidence:** 0.85 when right (14 tickets) against 0.53 when wrong (6 tickets). They are well
  apart, so a threshold between them works.

**Stretch.** With `COST_STRONG_MINOR = 12`, always-strong costs 240. The gate at 0.60 costs 152, a
37% saving instead of 62%. Sending everything costs 320, so that trap is still there. As the price
ratio falls, the saving shrinks. With 6 of 20 tickets escalated, the cascade costs 20 cheap calls
plus 6 strong ones, against 20 strong ones. That breaks even when the strong model costs about
**1.4 times** the cheap one. Well before that, the extra code is not worth it. The threshold is
a property of these twenty tickets. The price ratio is a property of the pattern. Take the ratio to
work.

## Lab 3 — The 40% token audit

| Cut | est. tokens | Share of baseline |
|---|--:|--:|
| baseline — `naive.txt` | 17,337 | 100% |
| cut 1 — drop the older account code | 9,055 | 52% |
| cut 2 — the rule, not all of `docs/` | 5,235 | 30% |
| cut 3 — a new chat (already done) | same | same |
| cut 4 — `PostingService.java` only | 648 | 4% |

These totals leave out the four instruction files Copilot adds by itself (924 tokens), because they
are the same in every cut. That is why the baseline is 17,337, not Lab 0's 18,261 for the same
`naive.txt`.

**Cut 3** was already applied: every check used a new chat. Its saving is the history you did not
send, about 44,000 est. tokens for six turns with the cut 2 file.

**What a right answer says:** no duplicate check exists, because `PostingService.post` always
creates a new posting. ADR-007 is accepted but not built. A duplicate is the same `clientReference`
and the same `valueDate`. A true retry gets the original posting back with `200 OK`. The same key
with a different amount, currency or account gets `409 Conflict`. The narrative never counts. A
unique index on the two fields closes the gap when two retries arrive at the same moment.

**Where it breaks:** cut 4. With one file, Copilot can see that nothing checks for duplicates. It
cannot know the team's rule, because the rule is written only in ADR-007. Watch for an answer that
proposes an `Idempotency-Key` header. ADR-007 rejected that design, because the team's two largest
callers do not pass headers through on a retry.

**The meter refusing a percentage** (naive → minimal): the code share falls from 73% to 42%, and
prose and instructions rise to 58%. `ctxmeter`'s error is different for each kind of file, so it
does not cancel across that change. Saved: 16,532 est. tokens. `--allow-mixed` prints the
percentage, and that is fine as long as you quote the mix with it.

**A good `mine.txt`** is close to `minimal.txt`: `PostingService.java`, `PostingRepository.java`
and ADR-007. Adding `PostingServiceTest.java` lets the answer also say that no test covers duplicates,
which makes it stronger.

## Lab 4 — Delete a model call

| Version | est. tokens |
|---|--:|
| The morning prompt with the data | 2,850 |
| The short prompt, counts supplied | 499 |
| Python | 0 |

Both token figures include the 389-token always-on instruction file. Without it, the drop is from
2,461 to 110 tokens.

The code version, every time:

```
unknown-account       11         26929300
invalid-amount         7      20050725802
currency-mismatch      5          3361400
total                 23      20081016502
```

**What the model is still good for:** deciding what to work on first. The seven `invalid-amount`
rejections are few, but two of them are over the posting limit, so they hold almost all of the
morning's money. The four unknown account ids (`ACC-CLIENT-003`, `ACC-CLIENT-01`, `ACC-PAYROL`,
`ACC-SUSPENCE`) are each one or two characters away from a real one, such as `ACC-PAYROL` for
`ACC-PAYROLL`. A model can spot that from the list. It points to bad account data in an upstream
system, not eleven separate problems. Those are judgements. The counts are not.
