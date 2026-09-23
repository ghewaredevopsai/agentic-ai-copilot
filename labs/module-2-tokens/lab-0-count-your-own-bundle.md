# Lab 0 — Count your own bundle

**About 6 minutes** · No Copilot needed · Measured, not scored

## What you will find out

What you can measure about spend on your own seat, and what you cannot.

By the end you can:

- say what a bundle of files costs in tokens, straight away, without waiting for GitHub's meter
- say whether your seat shows you a credit figure at all, and how old it is
- state how accurate `ctxmeter` is, and what it can never see

## What to look for

- **Which files are most of the bundle.** Check whether they have anything to do with the posting
  API.
- **What ten turns cost in total.** Each turn sends the whole chat so far again, so ten turns cost
  about eleven times one turn. Every agent chat grows this way. It is not a fault.
- **Which of three things happens** when you look for your credit figure. All three are results.

---

## Step 1 — Get ready

Do the [setup](README.md#setup-2-minutes) if you have not. You should be in your clone, at
`m3-start`:

```bash
cd ~/gb-labs/global-bank-account
git tag --points-at HEAD   # the list includes m3-start
```

## Step 2 — Compare two bundles

`everything.txt` is every file a "use my whole codebase" request can reach. `naive.txt` is what
most people attach on the first try: the source folder, the docs and the build file.

```bash
python $M2/tools/ctxmeter.py diff $M2/bundles/everything.txt $M2/bundles/naive.txt
```

Read the list of files before the totals. Answer two questions for yourself:

- Which files are the biggest in `everything.txt`? Are any of them about posting money?
- In `naive.txt`, how much of the list is the **older account code** (`controller/`, `service/`,
  `model/`)? `docs/architecture.md` says that code is out of scope for posting work.

`.github/copilot-instructions.md` shows as **always on**. You did not attach it, but Copilot sends
it with every request in this repository.

## Step 3 — Watch a chat grow

```bash
python $M2/tools/ctxmeter.py turns $M2/bundles/naive.txt --turns 10
```

Compare what **turn 1** sends with what **turn 10** sends: turn 10 is only a quarter bigger. Now
read the last column, the running total. That is what the whole ten-turn chat cost to send, and it
is about eleven times turn 1. Each turn sends the whole chat so far again.

## Step 4 — Now look at the other tool

Open your GitHub **billing and usage settings** and look for today's AI credit figure.

Three things can happen. **All three are results.** Write down which one you got:

1. **You see a number.** Note it, and note when it was last updated.
2. **You see a monthly total, but nothing for today.**
3. **You see nothing at all.** This is common on a company seat, where only an administrator sees
   usage.

If you got 3, you have found the limit this module is designed around. No lab needs a credit
figure.

## Step 5 — Read the calibration

Open [`tools/calibration.md`](tools/calibration.md). Read the **Result** table and the last section.
You will quote this tool's numbers all morning, so take ninety seconds to learn how accurate it is.

## Step 6 — Record

One paste creates the sheet:

```bash
mkdir -p $M2/../my-work
cat > $M2/../my-work/lab-0-record.md <<'EOF'
# Lab 0

everything.txt      ______ est. tokens
naive.txt           ______ est. tokens
Share of naive.txt that is the older account code: about ____%

turn 1 sends ______      turn 10 sends ______     10 turns in total ______

Credits visible on my seat?   yes / month only / no
If yes, last updated: ______

ctxmeter's error on one code file can be up to: ______  (from calibration.md)
What ctxmeter can never see: ____________________________________
EOF
```

Fill in the blanks in any editor and save.

## Key points

- **The build scripts and the older account code are most of what gets sent**, and none of it
  decides how a posting works. Every "just use my codebase" request sends it anyway.
- **Ten turns cost about eleven times one turn**, because each turn sends the whole chat again.
  This is why "start a new chat" is one of the cheapest savings you have.
- **`ctxmeter` gives a minimum.** It counts what you listed. It cannot see Copilot's hidden system
  prompt, Copilot's own search, or files the agent opens by itself. Every number from this module
  means "at least this much".
- **A token is not a credit.** Credits depend on the model's price and on how much of the request
  was cached. `ctxmeter` prints a money figure only if you give it a price, and then it labels the
  figure a what-if. A token count quoted as a bill is the fastest way to lose a finance team's
  trust.

## Stretch

Run the diff again with a price of $2.50 per million input tokens. `--rate` goes **before** `diff`:

```bash
python $M2/tools/ctxmeter.py --rate 2.50 diff $M2/bundles/everything.txt $M2/bundles/naive.txt
```

Now you have a money figure per turn. Before you put that
number in an email to your head of engineering, what else would you need to know? There are at
least three things, and two of them are in the footer the tool prints.
