#!/usr/bin/env python3
"""cascade_report - sweep the gate and show what each threshold costs.

    python $M2/tools/cascade_report.py              # the sweep
    python $M2/tools/cascade_report.py --record     # also write labs/my-work/lab-2-record.md

Runs the twenty supplied cases through `cascade.py`'s two functions at a range of
thresholds and prints accuracy, cost and escalation rate for each, against the two
baselines. No model is called and nothing touches the network, so every row is the
same for everyone in the room.

It does NOT edit cascade.py. Write your own `decide()` there first - the thinking is
the lab - then use this to see the whole curve at once instead of running the script
six times and copying numbers.

Standard library only.
"""

import importlib.util
import json
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parent.parent
MY_WORK = MODULE.parent / "my-work"
THRESHOLDS = [0.40, 0.50, 0.60, 0.65, 0.70, 0.80, 0.90, 1.01]


def load_cascade():
    spec = importlib.util.spec_from_file_location("cascade", MODULE / "tools" / "cascade.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    casc = load_cascade()
    cases = json.loads((MODULE / "data" / "triage-cases.json").read_text(encoding="utf-8"))["cases"]
    base = casc.baselines(cases)

    print()
    print("%-12s %9s %8s %11s   %s" % ("strategy", "accuracy", "cost", "escalated", "note"))
    print("-" * 70)
    print("%-12s %8.0f%% %8d %11s   %s"
          % ("always cheap", 100 * base["always_cheap"]["accuracy"],
             base["always_cheap"]["cost_minor"], "-", "wrong 3 times in 10"))
    print("%-12s %8.0f%% %8d %11s   %s"
          % ("always strong", 100 * base["always_strong"]["accuracy"],
             base["always_strong"]["cost_minor"], "all", "the baseline to beat"))
    print()

    strong = base["always_strong"]["cost_minor"]
    best = best_cost = None
    rows = {}
    plateau = []
    for t in THRESHOLDS:
        casc.decide = (lambda th: (lambda a, c, case: c < th))(t)
        r = casc.run(cases)
        note = ""
        if r["cost_minor"] > strong:
            note = "costs MORE than always-strong"
        elif r["accuracy"] >= base["always_strong"]["accuracy"]:
            if best is None:
                best, best_cost, note = t, r["cost_minor"], "cheapest at full accuracy"
                plateau.append(t)
            elif r["cost_minor"] == best_cost:
                note = "same cost - the plateau"
                plateau.append(t)
            else:
                note = "full accuracy, %.1fx the cost of %.2f" % (r["cost_minor"] / best_cost, best)
        rows[t] = r
        print("%-12s %8.0f%% %8d %10.0f%%   %s"
              % ("gate < %.2f" % t, 100 * r["accuracy"], r["cost_minor"],
                 100 * r["escalation_rate"], note))

    safe = plateau[len(plateau) // 2] if plateau else None
    if len(plateau) > 1:
        print()
        print("  %.2f is the cheapest, but it sits at the edge of a jump in accuracy."
              % plateau[0])
        print("  %.2f to %.2f cost the same. %.2f, in the middle, still works if the data shifts."
              % (plateau[0], plateau[-1], safe))

    right = [c["cheap_confidence"] for c in cases if c["cheap_answer"] == c["true_answer"]]
    wrong = [c["cheap_confidence"] for c in cases if c["cheap_answer"] != c["true_answer"]]
    print()
    print("  the assumption the whole pattern rests on:")
    print("    confidence when right %.2f  vs  when wrong %.2f  (over %d and %d cases)"
          % (sum(right) / len(right), sum(wrong) / len(wrong), len(right), len(wrong)))
    print("    if those two were equal, your gate would be a coin toss that costs money.")
    print()

    if "--record" in sys.argv:
        def row(t):
            r = rows[t]
            return "%.2f        %3.0f%%       %4d   %3.0f%%" % (
                t, 100 * r["accuracy"], r["cost_minor"], 100 * r["escalation_rate"])
        saving = ("%.0f%%" % (100 * (strong - best_cost) / strong)) if best else "____"
        MY_WORK.mkdir(exist_ok=True)
        (MY_WORK / "lab-2-record.md").write_text(f"""# Lab 2

threshold   accuracy   cost   escalated
{row(0.40)}
{row(0.60)}
{row(0.80)}
{row(1.01)}

Cheapest threshold at 100% accuracy: {best if best else '____'} ({saving} saving against always-strong)
Middle of the flat range: {safe if safe else '____'}
Escalate-everything cost {rows[1.01]["cost_minor"]} against always-strong's {strong}.
Confidence when right {sum(right)/len(right):.2f} vs when wrong {sum(wrong)/len(wrong):.2f}.

--- fill this in yourself ---

The threshold I would use, and why:
____________________________________________________________

Would this cascade work if the two confidence numbers were equal?  ______

At what price ratio between the two models does the cascade stop being worth
its complexity?
____________________________________________________________
""", encoding="utf-8")
        print("  wrote labs/my-work/lab-2-record.md - the numbers are filled in; answer the three questions")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
