# Lab 4 — Delete a model call

**About 12 minutes** · Copilot optional · Measured, not scored

## What you will find out

How to spot a model call that is really a calculation, replace it with code, and argue the case on
more than tokens.

By the end you can:

- separate the counting half of a prompt from the judgement half
- argue the case from **variance** (whether repeated runs agree), not only from cost
- say what you kept for the model, and why it really needs one

## What to look for

- **Whether three model runs agree with each other.** They often do not. Three Python runs always
  do.
- **That the grouping key already exists.** Every rejection already carries a fixed `reason`
  string, so grouping them is a lookup.
- **What is left after you take the counting away.** That part is worth paying for.

## The situation

Every morning, someone in payments operations pastes the list of postings the posting API rejected
since 07:00 into Copilot, with the prompt in
[`prompts/summarise-rejections.md`](prompts/summarise-rejections.md). Part of what it asks for is a
judgement. The rest is counting.

You are going to take the counting back.

Look at one rejection in [`data/rejections-morning.json`](data/rejections-morning.json). The
`reason` field is the fixed string the API returns, such as `unknown-account`. `docs/conventions.md`
in `global-bank-account` says: *"Reasons are stable strings — callers match on them."* The grouping
key existed before anyone wrote the prompt.

---

## Step 1 — Measure the prompt as it stands

From your clone:

```bash
cd ~/gb-labs/global-bank-account
python $M2/tools/ctxmeter.py count --absolute $M2/prompts/summarise-rejections.md $M2/data/rejections-morning.json
```

The total is roughly what one morning sends, before any answer comes back. It includes
`.github/copilot-instructions.md`, which Copilot sends with every request in this repository.

## Step 2 — Run it three times

In a **new chat** (Ask mode, base model), paste the prompt, then attach the data with
`#file:rejections-morning.json`. Do this **three times, in three new chats**.

Save the three replies in `$M2/../my-work/`, then answer two questions:

- Are the three **groupings** the same? (Do they all use the three reasons, or do some split
  `invalid-amount` into its three messages?)
- Are the three **counts and totals** the same? Check them against Step 3.

## Step 3 — Run the code version

```bash
python $M2/tools/rejections.py
```

```
reason             count   amount (minor)
unknown-account       11         26929300
invalid-amount         7      20050725802
currency-mismatch      5          3361400
total                 23      20081016502
```

The real output also lists each message under its reason. Open `tools/rejections.py`: the counting
is about ten lines, and it needs no model because the `reason` field already exists.

## Step 4 — Run the code three times

Same command, three times. Compare the three outputs.

## Step 5 — Decide what is left for the model

The counting is settled. What is left is **what to work on first, and why**. That depends on the
day, on who is on shift and on which clients are affected. That is a real judgement.

Write a much shorter prompt that asks only for the judgement, with the counts supplied. Save it as
`$M2/../my-work/prompt-short.txt`:

```text
Here are this morning's rejected postings, counted:
  unknown-account: 11 (4 different account ids, 3 of them one letter off a real one)
  invalid-amount: 7 (3 zero or negative, 2 over the posting limit, 2 same account)
  currency-mismatch: 5 (all from the USD client pool to an INR account)

Suggest what the duty operations analyst should work on first, and why, in under
80 words. If the counts alone do not justify a recommendation, say so.
```

## Step 6 — Measure the new prompt

```bash
python $M2/tools/ctxmeter.py count --absolute $M2/../my-work/prompt-short.txt
```

Compare the total with Step 1. Both totals include the same always-on instruction file.

## Step 7 — Record

```bash
cat > $M2/../my-work/lab-4-record.md <<'EOF'
# Lab 4

                          est. tokens   time taken   3 runs the same?
prompt as it stands       ______        ______       ___
Python                    0             ______       ___
short prompt, counts fed  ______        ______       ___

Tokens saved per morning: ______   Per year, at one run a working day: ______

The part I kept for the model, and why it needs a model:
____________________________________________________________
EOF
```

Fill in the blanks and save.

## Key points

- **The "3 runs the same?" column is the argument, not the token column.** Three model runs can give
  three different groupings. Three Python runs give one. You were paying for arithmetic that changes
  from run to run. Nobody would choose that if it were put to them as a choice. It arrives as "let's
  use AI for the morning report".
- **The saving adds up quietly.** One run a day is not a budget item. The same pattern across forty
  internal prompts is, and forty is not unusual for a department that has used AI for a year or two.
- **This is not an argument against using a model.** Step 5 is the point. The judgement half is hard
  and valuable, and worth every credit. Sending the counting along with it is the waste.
- **The grouping key was already in the codebase.** The team gave every rejection a fixed reason
  string, and later someone wrote a prompt that asks a model to find the groups. So the first
  question for any repeated prompt is: does this already exist?

## Stretch

Look at the older account code: `service/AccountServiceImpl.java` and `model/Account.java`. They
hold a balance as a `double`. Ask Copilot what is wrong with that, then check its answer against
`docs/adr/ADR-003-amounts-as-minor-units.md` yourself. Which problems are about money, and which are
about Copilot learning a bad pattern from your own codebase?
