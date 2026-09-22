# Lab 3 — The 40% token audit

**About 19 minutes** · Copilot needed for the checks · Measured, not scored

## What you will find out

How to cut what you send by at least 40% **and still get the right answer**. You will also find the
limit, by cutting past it.

By the end you can:

- run a token audit that checks the answer after every cut, not only at the end
- name the cut that broke the answer, and say why
- say what `ctxmeter` could not see, so your number holds up when someone questions it

## The question, the same for every cut

> Does the posting API stop a payment instruction that is retried from being posted twice? Answer
> yes or no and point to the code. Then say what the team's agreed design requires.

**The right answer has three parts:**

1. **No.** `PostingService.post` creates a new posting with a new id every time it is called. It
   never looks for an earlier posting.
2. It names **ADR-007**, the team's agreed design, which is accepted but **not yet built**. (An ADR
   is an architecture decision record: a short file that records a design decision and why it was
   made.)
3. It gives the rule: a duplicate has the **same `clientReference` and the same `valueDate`**. A
   true retry returns the original posting with `200 OK`. The same key with a different amount,
   currency or account is rejected with `409 Conflict`. The narrative text never counts.

An answer that proposes an **`Idempotency-Key` header** is wrong for this team. ADR-007 rejects
that design, because their two largest callers do not pass headers through on a retry.

## What to look for

- **The "answer still right?" column, not the token column.** An audit that only measures tokens
  proves you sent less, which was never in doubt.
- **Where it breaks.** If nothing you do breaks the answer, you did not cut hard enough, and you
  learned less than the person who did.

---

## Step 1 — See all four cuts before you run any

In your clone, at `m3-start`:

```bash
cd ~/gb-labs/global-bank-account
python $M2/tools/audit_report.py
```

```
           what changed                 est. tok  of baseline   answer still right?
------------------------------------------------------------------------------
baseline   what most people attach         17337       100%   ___
cut 1      drop the older account code      9055        52%   ___
cut 2      the rule, not all of docs/       5235        30%   ___
cut 3      a new chat (already done)        same       same   same as cut 2
cut 4      one file, far too little          648         4%   ___
```

The arithmetic is done. **The last column is yours**, and it is the only one that matters. The file
lists for each cut are in `$M2/bundles/`. The report also made `adr-007-rule.txt` in your clone: the
title, the status line, and the **Decision** and **Consequences** sections of ADR-007, which cut 2
uses.

The baseline here is 17,337, not Lab 0's 18,261 for the same `naive.txt`. These totals leave out the
four instruction files Copilot adds by itself (924 tokens), because they are the same in every cut.

## How to send each cut

Each cut is a list of up to 53 files. Attaching them one by one takes too long, so join each list
into one file and attach that:

```bash
for b in naive cut1-no-legacy cut2-rule-not-docs cut4-one-file; do
  python $M2/tools/ctxmeter.py pack $M2/bundles/$b.txt
done
```

For every check below:

- Use **Ask** mode, the **base model**, and a **new chat**.
- Close all editor tabs first, so Copilot does not add the open file.
- Type `#file:` and pick the `pack-….txt` file for that cut, then paste the question.
- After the answer, open the **references** list above it. Write down any file Copilot added **by
  itself**. The meter cannot see those files.
- If that list shows a `pack-` file for a different cut, or anything from the course's `solutions/`
  folder, the check is not fair. Delete that chat and ask again in a new one.

## Step 2 — Baseline

Attach `pack-naive.txt` and ask the question. Did the answer have all three parts? Mark the
baseline row.

## Step 3 — Cut 1: drop the older account code

Attach `pack-cut1-no-legacy.txt`: the same files without `controller/`, `service/`, `model/` and the
rest of the older account code. New chat, same question. Mark the row.

## Step 4 — Cut 2: the rule, not the whole docs folder

Attach `pack-cut2-rule-not-docs.txt`. It keeps the posting code and its tests. It swaps the whole
`docs/` folder, the resources and the build file for `adr-007-rule.txt`: ADR-007's title, its status
line and the part that states the rule. New chat, same question. Mark the row.

## Step 5 — Cut 3: start a new chat

You have already made this cut. Every check above used a new chat, so none of them sent any history.
That is why the cut 3 row says "same as cut 2": there is nothing new to ask.

The saving is the chat history you did not send, which no file list can show. The report printed
what six turns of history cost with the cut 2 file: about 44,000 tokens. The record sheet in Step 8
fills that figure in. In one long chat, every question would have paid for all the turns before it.

## Step 6 — Cut 4: go too far

First remove the other packs and the rule file, so Copilot cannot find them by itself:

```bash
rm -f adr-007-rule.txt pack-naive.txt pack-cut1-*.txt pack-cut2-*.txt
```

Attach **only `pack-cut4-one-file.txt`**: just `PostingService.java`. No tests, no docs, no ADR.
If the references list shows `docs/adr/ADR-007…`, Copilot found the rule by itself. Note that on
your sheet: the cut did not really happen.

**You are expected to break the answer here.** Copilot can still see there is no duplicate check.
It cannot know the team's rule, so it may invent one. A common invention is the `Idempotency-Key`
header that ADR-007 rejects. Mark the row, and write down *why* it broke. That sentence is the most valuable line
on your sheet.

## Step 7 — Watch the meter refuse a percentage

```bash
python $M2/tools/ctxmeter.py diff $M2/bundles/naive.txt $M2/bundles/minimal.txt
```

**It will not print a headline percentage.** Read the message. The naive bundle is mostly Java. In
the minimal one, more than half is prose and instructions. `ctxmeter` is less accurate on one kind of file
than another, so its error does not cancel across a change like this. Decide whether to run it again
with `--allow-mixed`, and be ready to say why that is, or is not, honest here.

## Step 8 — Record

```bash
python $M2/tools/audit_report.py --record
```

That writes `labs/my-work/lab-3-record.md` with every token figure filled in. **You fill in the
"answer still right?" column and the three questions at the end.**

Then remove the files the lab made in your clone:

```bash
rm -f adr-007-rule.txt pack-*.txt
git status --short        # should print nothing
```

## Key points

- **40% is the minimum.** Cut 2 sends 30% of the baseline, a 70% cut. If it kept the answer on your
  run and you stopped at 40%, you stopped early.
- **The biggest single cut was code nobody needed.** The older account code is almost half of what
  people attach, and `docs/architecture.md` already says it is out of scope for posting work.
- **The rule is small, and it is what makes the answer right.** Cut 2 keeps about 32 lines of
  ADR-007. Cut 4 drops them, and the answer changes from the team's design to a generic one. A
  missing rule is more costly than the tokens it saves.
- **`ctxmeter` refusing the percentage means the tool is working.** Using `--allow-mixed` is fine.
  Using it without reading the message is not.
- **The last line of the record sheet matters most at work.** Your percentage is a minimum measured
  on what you listed. The hidden system prompt, Copilot's own search, and any file it opened by
  itself are not in it. Someone senior will ask. Have the sentence ready.

## Stretch

Write your own file list, `$M2/../my-work/mine.txt`: the smallest set of paths that gets the right
answer in three runs out of three. Measure it with `ctxmeter.py diff` against `naive.txt`. Keep the
file. It answers "what should I attach for this kind of question?" once, for everyone who asks it
next.
