# Lab 1 — One matrix row you would defend

**About 16 minutes** · Works on any seat, including one that shows only **Auto** · Measured, not
scored

## What you will find out

Whether your opinion about which model to use holds up against data. The only fair way to test that
is to **write the opinion down first**.

By the end you can:

- write a prediction down before you look, and then score it
- read a model comparison without assuming the expensive model is better everywhere
- write one rule for choosing a model that you would defend, with a date to check it again

## What to look for

- **Where the reasoning model loses.** It is usually on the simple, mechanical task. Almost nobody
  predicts that.
- **Where four runs is not enough.** If two models are within one kept result of each other, four
  runs cannot tell them apart.
- **Your own confidence.** Most people get one prediction of three right.

The three model types in this lab are:

- **fast:** small and cheap
- **default:** what most seats use for everyday work
- **reasoning:** thinks step by step before it answers, and costs the most

---

## Step 1 — Predict before you open anything

Name your team's **three most common tasks** that you use AI for. For each one, predict which
model type gives the best **value for money**: fast, default or reasoning.

Write them down now:

```bash
mkdir -p $M2/../my-work
cat > $M2/../my-work/lab-1-record.md <<'EOF'
# Lab 1

task 1: ____________________  my prediction: ______
task 2: ____________________  my prediction: ______
task 3: ____________________  my prediction: ______
EOF
```

**Do not look ahead and then fill this in.** The lab is worthless if you do, and only you would
know.

## Step 2 — Open the data

First read the `provenance` block at the top of [`data/model-runs.json`](data/model-runs.json).
It says these 72 runs are **made up**. They are example data, not recorded measurements. They exist
so that this lab works offline and every room discusses the same numbers. Think about the patterns,
and **replace the file with your own recorded runs before you quote any row as evidence.**

Then print the summary:

```bash
python - <<'PY'
import json, collections, os
runs = json.load(open(os.path.expandvars("$M2/data/model-runs.json")))["runs"]
agg = collections.defaultdict(list)
for r in runs:
    agg[(r["task_type"], r["archetype"])].append(r)
print("%-20s %-10s %5s %7s %8s" % ("task", "model", "kept", "credits", "seconds"))
for (task, arch), rs in sorted(agg.items()):
    kept = sum(1 for r in rs if r["diff_kept"])
    cr = sum(r["approx_credits"] for r in rs) / len(rs)
    secs = sum(r["wall_seconds"] for r in rs) / len(rs)
    print("%-20s %-10s %2d/%-2d %7.1f %8.0f" % (task, arch, kept, len(rs), cr, secs))
PY
```

**kept** is how many of the four results a developer kept. **credits** and **seconds** are averages
per run.

## Step 3 — Score your predictions

How many of your three held? Most people get one.

## Step 4 — One real run

Pick **one** task type and run it once, for real, on whatever model your seat gives you. This one is
an `explain-code` task on `global-bank-account`. Use **Ask** mode and a **new chat**:

> Explain what `BalanceService.balanceMinorFor` does, and why this service works out a balance from
> ledger entries instead of storing it. Name the files you relied on.

Record how long it took, whether you would keep the answer, and the credits if your seat shows them.
**One run only.** You are not running a benchmark. You are checking that the example data is not
wildly different from what you see.

## Step 5 — Write the row

One row of a "which model for which task" guide, that you would defend to a colleague who disagrees:

```markdown
For ____________________ tasks we use the ______ model type,
because ____________________________________________
We check this again when ________________________________
```

The last line is required. A rule with no date to check it again is how a team ends up on last
year's choice.

## Step 6 — Record

Add the results to your sheet:

```bash
cat >> $M2/../my-work/lab-1-record.md <<'EOF'

predictions that held against the data: ___ of 3

The prediction I was most sure about, and what the data said:
____________________________________________________________

My real run: task ____________ time ____ kept? ___ credits ______

My row:
____________________________________________________________
EOF
```

Fill in the blanks and save.

## Key points

- **Writing the guess down first is the whole technique**, and it works for far more than models.
  It takes a minute. Afterwards you have either evidence or a surprise, and both are useful.
- **The reasoning model loses somewhere in this data**, usually on the mechanical task. It thinks too
  hard about a rename and changes files nobody asked it to. People expect the expensive model to be
  a little better everywhere. It is not.
- **Four runs per cell is few**, and the file says so. Where two models are close, four runs cannot
  separate them, so do not claim they do. Where one costs four times as much for the same result,
  four runs is enough.
- **You did not run three models yourself, and that is deliberate.** Many seats show only **Auto**,
  so a live three-model comparison would not work for everyone. What mattered here was your
  prediction.

## Stretch

Sort the data by **credits per kept result** instead of by credits. Does any model type change
place? That ratio, what you paid for work you actually used, is closer to what your finance team
means by cost than anything on the billing page.
