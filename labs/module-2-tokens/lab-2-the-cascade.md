# Lab 2 — The cascade, and what it saved

**About 15 minutes** · No Copilot, no network · Measured, not scored

## What you will find out

How to set the **gate**: the rule that decides when the cheap model's answer is not good enough.
And what a badly set gate costs.

By the end you can:

- find the threshold where a cascade matches the strong model's accuracy, and the threshold where it
  costs more than not using a cascade at all
- check whether the cheap model's confidence matches whether it is right, and say what happens if
  it does not

## What to look for

- **A flat range, not a single point.** Is there a range of thresholds that all cost the same? A
  threshold in the middle of a flat range is safe. A threshold at the edge of a sudden jump only
  fits this sample.
- **The last row.** Sending every case to the strong model reaches 100% accuracy. How does its cost
  compare with using the strong model alone? Only the cost column can tell you.
- **Confidence when right, against confidence when wrong.** If those two were equal, the whole
  pattern fails. Almost nobody checks.

## The situation

The payments operations team gets tickets about payment instructions: an unknown account, a
currency mismatch, a suspected duplicate and so on. Each ticket must go to one of six queues.

You have **twenty tickets** and two "models". The models are ordinary Python functions with a known
accuracy and a known price, so every number in the room is the same. The cheap model costs 4 units a
call. The strong model costs 48, twelve times as much, and it is always right.

Your job is the gate.

---

## Step 1 — Run it unchanged

```bash
python $M2/tools/cascade.py
```

The gate sends nothing to the strong model yet. So you get the cheap model's accuracy at the cheap
model's price, and a message that says so.

## Step 2 — Read the two baselines

From that output:

- **always cheap:** 70% accurate, cost 80
- **always strong:** 100% accurate, cost 960

Everything you do next lands between those two rows.

## Step 3 — Write a simple gate

Open `tools/cascade.py` in this folder and find `decide()`. Replace its last line, `return False`,
with:

```python
return confidence < 0.5
```

Run it again:

```bash
python $M2/tools/cascade.py
```

It sends one ticket to the strong model, and five wrong answers still get through. Change `0.5` to a
higher number of your choice and run it again. Stop when you reach 100% accuracy. Write down the
threshold and the cost.

Step 4 shows you whether you found the cheapest one.

## Step 4 — See every threshold at once

```bash
python $M2/tools/cascade_report.py
```

It prints one row per threshold: accuracy, cost and how many tickets went to the strong model.

**Find the cheapest threshold that still reaches 100%.** Was it the one you found in Step 3? Then
look for a range of thresholds with the same cost. The report names both: the cheapest one, and the
middle of the flat range. The cheapest one sits at the edge of a jump in accuracy, so it only fits
this sample. The middle one still works if the data shifts a little. That is the one to use.

This report does not change `cascade.py`. Your gate from Step 3 stays as you wrote it.

## Step 5 — Look hard at the last row

`gate < 1.01` sends every ticket to the strong model. Compare its cost with always-strong's 960.

**It costs more.** You paid for the cheap answer twenty times and threw it away twenty times. The
accuracy column still says 100%, so the answers never show the waste. **Only the cost column
does.**

Write that number down. It is the most important row in the lab.

## Step 6 — Check what the pattern depends on

Does the cheap model's confidence actually match whether it is right?

```bash
python - <<'PY'
import json, os
cases = json.load(open(os.path.expandvars("$M2/data/triage-cases.json")))["cases"]
right = [c["cheap_confidence"] for c in cases if c["cheap_answer"] == c["true_answer"]]
wrong = [c["cheap_confidence"] for c in cases if c["cheap_answer"] != c["true_answer"]]
print("when right: %.2f average over %d tickets" % (sum(right)/len(right), len(right)))
print("when wrong: %.2f average over %d tickets" % (sum(wrong)/len(wrong), len(wrong)))
PY
```

If those two numbers were equal, your gate would be a coin toss that costs money.

## Step 7 — Record

```bash
python $M2/tools/cascade_report.py --record
```

That writes `labs/my-work/lab-2-record.md`, with every number from the report already filled in.
**You answer the three questions at the end**: the threshold you would use and why, what equal
confidence would mean, and the price ratio.

Then put `cascade.py` back as it was. Your edit is in the course clone, and a later `git pull` of the
course would stop on it:

```bash
git -C ~/agentic-ai-copilot checkout labs/module-2-tokens/tools/cascade.py
```

## Key points

- **There is a threshold where you get the strong model's accuracy for about a third of its
  price.** That is the pattern working. It saves more than any prompt technique in this course.
- **Send everything to the strong model and you pay more than always-strong.** The accuracy column
  still says 100%, so nothing in the answers tells you. Only the cost column does, and that is the
  reason to have one.
- **Step 6 is the check nobody does.** If the cheap model is as confident when it is wrong as when
  it is right, your gate picks cases at random and the cascade is worse than either model alone. A
  cheap model that is confidently wrong cannot be used in a cascade. It can only be replaced.
- **Nothing here called a real model.** Anyone in the room can reproduce every number on your sheet.
  With real models that stops being true, and your threshold becomes something you measure again,
  not a fixed value.

## Stretch

In `cascade.py`, change `COST_STRONG_MINOR` from 48 to 12, so the strong model costs three times as
much instead of twelve. Run the report again, then put the file back with the same
`git -C ~/agentic-ai-copilot checkout …` command as in Step 7. Does your threshold still make sense? At what price
ratio does the cascade stop being worth the extra code? Take that ratio back to work, not the
threshold.
