from nbgen import SETUP, code, md, write

cells = [
md("""
# Lab R.3 &mdash; Long-term memory: what to write, what to forget

**Day 2 &middot; Module 3 &mdash; RAG, Vector Stores & Agent Memory** &nbsp;|&nbsp; **Time:** about 25 min

In Module 4, the agent's memory was its message list, and that list is gone when the run ends.
**Long-term memory** is a store that lasts across sessions. The AskOps agent can then remember
that you like numbered steps, or who the payments on-call lead is.

A memory store that keeps everything soon fills with guesses, secrets and old facts. So it
needs two sets of rules:

- a **write policy**: what may be saved;
- an **eviction policy**: what is removed, and when.

You write both in this lab. The store is a Chroma collection, so later sessions find memories
by meaning, the same way you searched runbooks in Lab R.1.

> **How this lab works.** Replace every `BLANK`, then run the **Self-check** cell below it. A cell
> that uses an empty `BLANK` stops with `NameError: name 'BLANK' is not defined`. That is expected.
> Time is simulated: `today` is a day number, so you can jump 45 days ahead in one line.
> Nothing in this lab calls the chat model.
"""),
code(SETUP),

md("""
## Section 1 &mdash; The write policy

Each memory the agent wants to save is a dict like this:

```python
{"key": "oncall-lead:payments", "kind": "fact", "confirmed": True,
 "text": "The payments on-call lead is Priya."}
```

- `key` names **what** the memory is about. Two memories with the same key are about the same thing.
- `kind` is `preference`, `fact` or `outcome` (how an incident ended). Anything else, such as a
  `guess`, is not worth keeping.
- `confirmed` is `True` only when a person said it or confirmed it. A model's own guess is `False`.

Write `should_write()`. It returns `False` for each of the three reasons below, and `True` otherwise.
"""),
code('''
import re

TTL_DAYS = {"preference": 365, "fact": 90, "outcome": 30}   # how long each kind may live
SECRET = re.compile(r"password|passwd|token|api[ _-]?key|\\b\\d{12,19}\\b", re.I)  # last part: card numbers

def should_write(item: dict) -> bool:
    if item["kind"] not in TTL_DAYS:           # a guess or small talk
        return False
    if «not item["confirmed"]»:                  # the model inferred it; nobody confirmed it
        return False
    if «SECRET.search(item["text"])»:            # never store a secret or a card number
        return False
    return True
'''),
code('''
# --- Self-check: Section 1
check("a confirmed preference is written",
      lambda: should_write({"key": "style", "kind": "preference", "confirmed": True,
                            "text": "Give answers as numbered steps."}))
check("a model's guess is not",
      lambda: not should_write({"key": "cause", "kind": "guess", "confirmed": False,
                                "text": "The database is probably slow."}))
check("an unconfirmed fact is not",
      lambda: not should_write({"key": "oncall-lead:payments", "kind": "fact", "confirmed": False,
                                "text": "I think the payments on-call lead is Ravi."}))
check("a password is not, even when confirmed",
      lambda: not should_write({"key": "db", "kind": "fact", "confirmed": True,
                                "text": "The report DB password is Winter2026."}))
check("a card number is not",
      lambda: not should_write({"key": "card", "kind": "fact", "confirmed": True,
                                "text": "The test card is 4111111111111111."}))
'''),

md("""
## Section 2 &mdash; Replace on conflict, then evict

`MemoryStore` saves each memory with its `key` as the Chroma id. Chroma's `upsert()` adds a new
id, or **replaces** the item that already has that id. So a newer fact about the same key
replaces the older one, and the store never holds two different on-call leads.

Every item also stores two day numbers: `created` and `last_used`. Eviction uses them in two ways:

1. **Time to live (TTL).** An item is expired when `today - created` is more than the TTL for its kind.
2. **Size cap.** If more than `MAX_ITEMS` remain, delete the ones used **least recently** first.

Fill the three `BLANK`s.
"""),
code('''
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

MAX_ITEMS = 6

class MemoryStore:
    def __init__(self):
        client = chromadb.Client()
        try:
            client.delete_collection("memory")
        except Exception:
            pass
        self.col = client.create_collection("memory", embedding_function=DefaultEmbeddingFunction(),
                                            metadata={"hnsw:space": "cosine"})

    def write(self, item: dict, today: int) -> bool:
        if not should_write(item):
            return False
        self.col.upsert(ids=[«item["key"]»], documents=[item["text"]],
                        metadatas=[{"kind": item["kind"], "created": today, "last_used": today}])
        self.evict(today)
        return True

    def expired(self, meta: dict, today: int) -> bool:
        return «today - meta["created"] > TTL_DAYS[meta["kind"]]»

    def evict(self, today: int) -> list[str]:
        got = self.col.get()
        items = list(zip(got["ids"], got["metadatas"]))
        gone = [i for i, m in items if self.expired(m, today)]
        alive = [(i, m) for i, m in items if i not in gone]
        if len(alive) > MAX_ITEMS:
            alive.sort(key=lambda pair: pair[1]["last_used"])          # least recently used first
            gone += [i for i, _ in alive[: «len(alive) - MAX_ITEMS»]]
        if gone:
            self.col.delete(ids=gone)
        return gone

    def recall(self, question: str, today: int, k: int = 2) -> list[str]:
        """Given. Find memories by meaning, and mark them as used today."""
        if self.col.count() == 0:
            return []
        res = self.col.query(query_texts=[question], n_results=min(k, self.col.count()))
        for i, m in zip(res["ids"][0], res["metadatas"][0]):
            self.col.update(ids=[i], metadatas=[{**m, "last_used": today}])
        return res["documents"][0]

    def forget(self, key: str) -> None:
        """Given. Delete on request: a person asks the agent to forget something."""
        self.col.delete(ids=[key])

    def keys(self) -> list[str]:
        return sorted(self.col.get()["ids"])
'''),

md("""
## Section 3 &mdash; Run a month of sessions

The cell below plays three sessions with the AskOps agent. Read what each one tries to save,
and predict what the store holds at the end. Then run it.
"""),
code('''
mem = MemoryStore()

# Day 1 - first session
day1 = [
    {"key": "style",                "kind": "preference", "confirmed": True,  "text": "Give answers as numbered steps."},
    {"key": "cause:INC-9001",       "kind": "guess",      "confirmed": False, "text": "The 502s are probably a bad load balancer."},
    {"key": "db",                   "kind": "fact",       "confirmed": True,  "text": "The report DB password is Winter2026."},
    {"key": "oncall-lead:payments", "kind": "fact",       "confirmed": True,  "text": "The payments on-call lead is Priya."},
    {"key": "outcome:INC-9001",     "kind": "outcome",    "confirmed": True,  "text": "INC-9001 was fixed by rolling back the 14:00 release."},
]
print("Day 1 written:", [m["key"] for m in day1 if mem.write(m, today=1)])

# Day 10 - the on-call lead changes
mem.write({"key": "oncall-lead:payments", "kind": "fact", "confirmed": True,
           "text": "The payments on-call lead is Arjun."}, today=10)
print("Day 10 recall:", mem.recall("Who leads payments on-call?", today=10, k=1))

# Day 45 - a new session, a month later
print("Day 45 evicted:", mem.evict(today=45))
day45 = mem.keys()
print("Day 45 store:  ", day45)
'''),
code('''
# --- Self-check: Section 3
check("day 1 kept 3 of the 5 memories (the guess and the password were refused)",
      lambda: day45 is not None and "db" not in mem.keys() and "cause:INC-9001" not in mem.keys())
check("there is one on-call lead, and it is the newer one",
      lambda: day45 is not None and mem.col.get(ids=["oncall-lead:payments"])["documents"] == ["The payments on-call lead is Arjun."])
check("the 30-day incident outcome expired by day 45",
      lambda: day45 is not None and "outcome:INC-9001" not in day45)
check("the preference and the fact are still there",
      lambda: day45 == ["oncall-lead:payments", "style"])
'''),

md("""
## Section 4 &mdash; The size cap, and forgetting on request

From day 50 the agent learns one new fact a day, eight in all, but the store may hold only 6
items. On day 54, halfway through, the engineer asks a question that **uses** the style
preference. Predict which items the cap removes, then run the cell.
"""),
code('''
for n in range(1, 9):
    today = 49 + n
    if today == 54:
        mem.recall("How should you format the answer?", today=today, k=1)   # uses "style"
    mem.write({"key": f"service-owner:{n}", "kind": "fact", "confirmed": True,
               "text": f"Service {n} is owned by team {n}."}, today=today)

after_cap = mem.keys()
print(len(after_cap), "items:", after_cap)
'''),
code('''
# --- Self-check: the cap
check("the store never holds more than MAX_ITEMS",
      lambda: len(after_cap) <= MAX_ITEMS)
check("the preference survived, because it was used on day 54",
      lambda: "style" in after_cap)
check("the on-call lead went first: it was last used on day 10",
      lambda: "oncall-lead:payments" not in after_cap)
check("then the oldest service owners, and the newest stayed",
      lambda: "service-owner:1" not in after_cap and "service-owner:8" in after_cap)
'''),
md("""
Last rule: **delete on request**. Privacy rules give people the right to ask a system to forget
what it stored about them. The engineer now says *"Forget how I like my answers."*
"""),
code('''
mem.forget("style")
after_forget = mem.keys()
print("after forget:", after_forget)

# --- Self-check: forget
check("forget() removed the preference, and nothing else",
      lambda: "style" not in after_forget and len(after_forget) == len(after_cap) - 1)
score()
'''),
md("""
## Your turn (if you have time)

1. The store refuses the model's guess. Some teams save guesses too, with `confirmed: False`, and
   show them as *"unconfirmed"*. What could go wrong if a later session reads one as a fact?
2. Replace-on-conflict only works when two memories share a **key**. What happens if one session
   saves `oncall-lead:payments` and another saves `payments-oncall`? How could the agent choose
   keys more reliably?
3. Where would these rules live in the Module 4 agent loop: before the model call, after it, or
   in a tool such as `save_memory`?
"""),
]

if __name__ == "__main__":
    write("lab-r3-memory-policies.ipynb", cells)
