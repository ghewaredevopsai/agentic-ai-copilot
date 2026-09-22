# Module 2 labs — Token optimisation and model selection

Five labs. Each one measures a number before a change and after it. Nothing is scored.

The slides for this module are
[`presentation/module-2-token-optimization.html`](../../presentation/module-2-token-optimization.html).
Each lab follows the part of the deck that it practises.

| Lab | Time | What you do | What you record |
|---|:--:|---|---|
| [0 · Count your own bundle](lab-0-count-your-own-bundle.md) | 6 min | Measure two bundles. Find out what your seat shows you about credits | Bundle sizes, how a chat grows, credits visible or not |
| [1 · One matrix row](lab-1-one-matrix-row.md) | 16 min | Predict first, then read 72 recorded runs | How many of your three predictions held |
| [2 · The cascade](lab-2-the-cascade.md) | 15 min | Write the rule that sends hard cases to the strong model. Find where it pays | Accuracy and cost at four thresholds |
| [3 · The 40% token audit](lab-3-the-40-percent-audit.md) | 19 min | Four cuts. Check the answer after each one | Tokens, and whether the answer held, at every cut |
| [4 · Delete a model call](lab-4-delete-a-model-call.md) | 12 min | Replace the counting half of a prompt with a few lines of Python | Tokens, and whether three runs agree |

**Words used in these labs**

- **Token:** the unit a model reads and writes. A token is roughly three quarters of an English word.
- **Bundle:** the set of files you send with one request. The files in [`bundles/`](bundles/) list them.
- **Always on:** a file Copilot sends with every request, whether you attached it or not. In
  `global-bank-account` that is `.github/copilot-instructions.md`.
- **Cascade:** try the cheap model first. Send a case to the strong model only when a rule says so.
- **AI credits:** what GitHub charges Copilot usage in. A credit is not a token. It depends on the
  model's price and on how much of the request was cached.

## Setup (2 minutes)

You need the `global-bank-account` clone from Module 1, and **Python 3.14**. Nothing is installed,
and no lab tool reaches the network.

In a Git Bash or terminal window, point `M2` at this folder, then go to your clone at the Module 1
tag that has the team's docs:

```bash
export M2=~/agentic-ai-copilot/labs/module-2-tokens     # change this to where your course folder is
cd ~/gb-labs/global-bank-account
git fetch --tags --force
git switch --detach m3-start
python $M2/tools/ctxmeter.py diff $M2/bundles/everything.txt $M2/bundles/naive.txt
```

If the last command prints two lists of files and a line starting `saved`, you are ready.

Keep that terminal open. Every command in these labs uses `$M2`. If you open a new terminal, run the
`export` line again.

## How these labs work

- **Two tools that do not agree.** `ctxmeter` answers straight away. It counts only the files you
  list. Your billing page is the true record of money, but it is late and it only shows totals. Keep
  the two apart: `ctxmeter` shows that a cut worked, and the billing page shows what you spent.
- **Your record sheet is the result.** Each lab ends with a `lab-N-record.md` in `labs/my-work/`.
  That folder is yours and is not committed. With the sheet you can back up a cost claim to someone
  who was not in the room.
- **Labs 0 and 2 need no Copilot.** They are arithmetic on supplied data, so they work on a
  locked-down machine and everyone gets the same numbers.
- **No credit figure on your seat?** That does not stop any lab. Lab 0 asks you to write down what
  you can see. The other labs do not depend on it.

## What is in this folder

| Path | What it is |
|---|---|
| `tools/ctxmeter.py` | Estimates the tokens in a bundle. Read [`tools/calibration.md`](tools/calibration.md) for how accurate it is on this repository |
| `tools/cascade.py` | Lab 2. Two pretend models and the rule you write |
| `tools/cascade_report.py`, `tools/audit_report.py` | Print the whole table for Labs 2 and 3, so you do not copy numbers by hand |
| `tools/rejections.py` | Lab 4. Counts the morning's rejected postings without a model |
| `bundles/` | The file lists that Labs 0 and 3 measure |
| `data/` | The cases for Lab 2, the recorded runs for Lab 1, and the rejected postings for Lab 4 |
| `prompts/` | The morning prompt for Lab 4 |
| [`solutions/`](solutions/README.md) | A reference answer for every lab. Look whenever you want |
| [`learning-outcomes.md`](learning-outcomes.md) | What you should be able to do after each part. Tick them off |

## When the labs end

Lab 3 leaves files in your clone. Remove them:

```bash
cd ~/gb-labs/global-bank-account
rm -f adr-007-rule.txt pack-*.txt
git status --short        # should print nothing
```

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
