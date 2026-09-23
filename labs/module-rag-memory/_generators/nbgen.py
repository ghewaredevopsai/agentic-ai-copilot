"""Build a lab notebook and its solution from one source.

In a code cell, «answer» becomes BLANK in the lab and `answer` in the solution.
Run the lab generators from this folder:  python build_all.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
BLANK_RE = re.compile(r"«(.+?)»")

SETUP = '''# ---------------------------------------------------------------- Setup: run me first
import os, sys, warnings
warnings.filterwarnings("ignore")          # the model libraries print a lot on first import
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# rag_kit.py sits in the lab folder, one level up from solutions/
for _d in (os.getcwd(), os.path.dirname(os.getcwd())):
    if os.path.exists(os.path.join(_d, "rag_kit.py")):
        sys.path.insert(0, _d)
        break
import rag_kit as kit

# ---- self-check plumbing -------------------------------------------------
_results = []

def check(name, fn, hint=""):
    """Prints [PASS], [FAIL] or [TODO] for one check. A BLANK you have not filled gives [TODO]."""
    try:
        ok = bool(fn())
    except NameError:
        print(f"[TODO] {name}")        # a BLANK, or a cell above that has not run yet
        _results.append(None)
        return
    except Exception as exc:
        print(f"[FAIL] {name} -- {type(exc).__name__}: {exc}")
        _results.append(False)
        return
    print(("[PASS] " if ok else "[FAIL] ") + name + ("" if ok or not hint else f"\\n       hint: {hint}"))
    _results.append(ok)

def score():
    passed = sum(1 for r in _results if r)
    todo = sum(1 for r in _results if r is None)
    print(f"Score: {passed}/{len(_results)}" + (f"   ({todo} still TODO)" if todo else ""))

print("Setup done. Chunks in the runbook set:", len(kit.all_chunks()))
'''


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n")}


def code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n")}


def _render(cells: list[dict], solution: bool) -> dict:
    out = []
    for c in cells:
        c = dict(c)
        if c["cell_type"] == "code":
            c["source"] = BLANK_RE.sub((lambda m: m.group(1)) if solution else "BLANK", c["source"])
        src = c["source"]
        c["source"] = [line + "\n" for line in src.split("\n")[:-1]] + [src.split("\n")[-1]]
        out.append(c)
    return {"cells": out, "nbformat": 4, "nbformat_minor": 5,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                        "name": "python3"},
                         "language_info": {"name": "python", "version": "3.12"}}}


def write(name: str, cells: list[dict]) -> None:
    (LAB_DIR / "solutions").mkdir(exist_ok=True)
    for solution, path in ((False, LAB_DIR / name), (True, LAB_DIR / "solutions" / name)):
        path.write_text(json.dumps(_render(cells, solution), indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print("wrote", path.relative_to(LAB_DIR))
