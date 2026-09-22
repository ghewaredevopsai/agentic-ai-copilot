#!/usr/bin/env python3
"""rejections - this morning's rejected postings, counted without a model.

    python $M2/tools/rejections.py

Every rejection already carries a stable `reason` string (docs/conventions.md,
"Errors"), so grouping them is a lookup, not a judgement. Standard library only.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "rejections-morning.json"

rows = json.loads(DATA.read_text(encoding="utf-8"))["rejections"]
count = Counter(r["reason"] for r in rows)
amount = defaultdict(int)
details = defaultdict(Counter)
for r in rows:
    amount[r["reason"]] += r["amountMinor"]
    details[r["reason"]][r["detail"]] += 1

print("%-18s %5s %16s" % ("reason", "count", "amount (minor)"))
for reason, n in count.most_common():
    print("%-18s %5d %16d" % (reason, n, amount[reason]))
    for detail, times in sorted(details[reason].items()):
        print("    %2d x %s" % (times, detail))
print("%-18s %5d %16d" % ("total", len(rows), sum(amount.values())))
