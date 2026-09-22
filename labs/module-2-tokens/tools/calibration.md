# ctxmeter calibration

`ctxmeter` estimates tokens. It is not a tokenizer. This page shows how far off it is, so you know
how much to trust the numbers it prints.

**Measured 22 September 2026** against two real tokenizers, `tiktoken`'s `o200k_base` and
`cl100k_base`. The reference was the average of the two. The files measured were every file in
`global-bank-account` at tag `m3-start`: 62 files.

## Result

| Content class | Files | Error on the class total | Worst file, under | Worst file, over |
|---|--:|--:|--:|--:|
| code (`.java`, `.sql`) | 43 | **&minus;0.4%** | &minus;14.4% | +23.4% |
| prose (`.md`) | 12 | **&minus;0.1%** | &minus;7.0% | +9.0% |
| data (`.xml`, `.yml`) | 3 | **&minus;0.2%** | &minus;8.1% | +17.4% |
| other (`mvnw`, `.properties`) | 4 | **&minus;0.4%** | &minus;2.3% | +8.8% |
| **Whole repository** | 62 | **&minus;1.7%** against `o200k_base`, **+1.0%** against `cl100k_base` | | |

**How to read it:** the total for a bundle of files is reliable. Any single file can be off by
about 20%. So use `ctxmeter` for bundles and for before-and-after differences. Do not use it to
judge one file.

## The two real tokenizers disagree too

On this repository, `o200k_base` counts **2.8% more** tokens than `cl100k_base`. Different models
use different tokenizers, and you cannot know which one Copilot's model uses on a given day.
So the useful habit is to measure your own before-and-after difference with one tool, the same
way each time.

## What was fitted

`ctxmeter` splits text into pieces, the way a real tokenizer starts, and charges each piece. Four
constants control that:

| Constant | Value | Meaning |
|---|--:|---|
| `LONG_PIECE` | 8 | a piece longer than this is split by a real tokenizer |
| `CHARS_PER_SUBWORD` | 6 | ...into pieces of about this many characters |
| `WHITESPACE_RUN` | 12 | a run of spaces costs about one token per this many |
| `PUNCTUATION_RUN` | 3 | so does a run of brackets, quotes and commas |

Then one correction factor per content class:

```python
CALIBRATION = {"code": 0.76, "data": 0.92, "prose": 0.85, ...}
```

The four constants were first fitted on a Python repository. On Java they over-counted by
**+15%**, because Java has deeper indentation and longer names. The class factors were then
re-fitted on this repository, which brought each class total to within 0.5%.

## Run the check yourself

`ctxmeter` uses only the Python standard library. The real tokenizer is installed in a separate
virtual environment, used once and thrown away. Run this from inside your `global-bank-account`
clone:

```bash
python -m venv /tmp/tkvenv
/tmp/tkvenv/bin/pip install tiktoken
/tmp/tkvenv/bin/python - <<'PY'
import os, sys; sys.path.insert(0, os.path.expandvars("$M2/tools"))
import tiktoken
from ctxmeter import estimate_tokens, classify, REPO
enc = tiktoken.get_encoding("o200k_base")
for p in sorted(REPO.rglob("*")):
    if p.is_file() and ".git" not in p.parts:
        t = p.read_text(encoding="utf-8", errors="replace")
        if t.strip():
            e, r = estimate_tokens(t, classify(p)), len(enc.encode(t))
            print("%-60s %+6.1f%%" % (p.relative_to(REPO), 100.0 * (e - r) / r))
PY
```

On Windows, the venv's Python is `/tmp/tkvenv/Scripts/python`.

## What it still cannot see

The biggest errors in practice are not in the arithmetic. `ctxmeter` cannot see:

- the hidden system prompt that Copilot adds
- the files Copilot's own search adds to the request
- any file the agent decides to open once it starts working
- the tool definitions, in the exact form they are sent

So every number `ctxmeter` prints is a **minimum**. This page tells you how good the arithmetic is
on the files you listed. It tells you nothing about what else was sent with them.
