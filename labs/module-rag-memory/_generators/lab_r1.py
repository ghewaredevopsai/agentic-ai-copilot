from nbgen import SETUP, code, md, write

cells = [
md("""
# Lab R.1 &mdash; Hybrid retrieval

**Day 2 &middot; Module 3 &mdash; RAG, Vector Stores & Agent Memory** &nbsp;|&nbsp; **Time:** about 25 min

In Module 3, AskOps searched runbooks by the words in their titles. In this lab you search the
full runbook text in two ways, by meaning and by exact words, and then merge the two result lists.

### What you will do
1. Look at the chunks and their metadata, and filter a search with metadata.
2. Find two questions where the two searches disagree.
3. Write the merge (RRF) and measure hybrid search on 14 questions.

> **How this lab works.** Replace every `BLANK` with your code, then run the **Self-check** cell
> below it. A check prints `[PASS]`, `[FAIL]` or `[TODO]`. `[TODO]` means a `BLANK` is still
> there. A cell that uses an empty `BLANK` stops with `NameError: name 'BLANK' is not defined`.
> That is expected: fill the `BLANK` and run the cell again. Nothing in this lab calls the chat model, so the results are the same every time.
> The helpers are in `rag_kit.py` next to this notebook. You can open it and read it.
"""),
code(SETUP),

md("""
## Section 1 &mdash; Chunks and metadata

The runbooks are in `data/runbooks/`, one Markdown file each. `rag_kit` splits every runbook at
its `##` headings, so each chunk is one section: *Symptoms*, *Checks*, *Fix* or *Escalation*.
Every chunk starts with the runbook id and title, so a chunk that says *"Restart one pod at a
time"* still says which problem it fixes.

Each chunk also carries **metadata**: labels that are stored next to the text. You can filter
on them, cite them, and use them for access control.
"""),
code('''
chunks = kit.all_chunks()
print(len(chunks), "chunks from", len(kit.load_runbooks()), "runbooks\\n")
print(chunks[0]["text"], "\\n")
print(chunks[0]["metadata"])
'''),
md("""
Now build the vector store. `build_collection()` embeds every chunk with Chroma's default
embedding model and stores it in memory. It takes a few seconds the first time.

Then write two `where` filters. Chroma takes a dict of `{field: value}` and matches it against
the metadata you stored.

- `ledger_only()` keeps the search inside the **ledger** service.
- `ops_only()` keeps out **restricted** runbooks. A normal on-call engineer uses this filter.
  One runbook, RB-111, is marked `access: restricted`.
"""),
code('''
col = kit.build_collection(chunks)

def ledger_only() -> dict:
    return {"service": «"ledger"»}

def ops_only() -> dict:
    return «{"access": "ops"}»

def show(ids):
    for i in ids:
        print("  ", i)

q = "We need to run SQL directly on the production database during an incident"
print("No filter:");   show(kit.vector_search(col, q, k=3))
print("ops_only():");  show(kit.vector_search(col, q, k=3, where=ops_only()))
'''),
code('''
# --- Self-check: Section 1
q = "We need to run SQL directly on the production database during an incident"
check("with no filter, the restricted runbook RB-111 comes first",
      lambda: kit.runbook_of(kit.vector_search(col, q, k=1)[0]) == "RB-111")
check("the ledger filter returns only ledger chunks",
      lambda: all(i.startswith("RB-107") for i in kit.vector_search(col, "service is down", k=4, where=ledger_only())))
check("the ops filter never returns RB-111",
      lambda: not any(i.startswith("RB-111") for i in kit.vector_search(col, q, k=10, where=ops_only())),
      "a filter is how retrieval respects access rights: the model never sees what it may not show")
'''),

md("""
## Section 2 &mdash; Two searches that disagree

`kit.BM25` is **keyword search**. It is the classic formula used by Elasticsearch and OpenSearch.
A chunk scores high when it contains the question's words, and more when those words are rare.
Vector search compares **meaning**, so it does not need the same words.

Run the two questions below and read the top 3 of each search. You do not need to write
anything in this section.
"""),
code('''
bm25 = kit.BM25(chunks)

def compare(question):
    v = kit.vector_search(col, question, k=3)
    b = bm25.search(question, k=3)
    print(f"Q: {question}")
    print(f"  vector : {v}")
    print(f"  keyword: {b}\\n")

compare("OOMKilled at month end")
compare("app killed because it used too much RAM")
'''),
md("""
**What to notice.** RB-113 is *Transaction service runs out of memory*.

- For **"OOMKilled at month end"**, keyword search finds RB-113 first, because `OOMKilled` is a
  rare, exact word. Vector search prefers the nightly batch runbook, because "month end" and
  "batch" have a similar meaning.
- For **"too much RAM"**, it is the other way round. No runbook contains the word "RAM", so
  keyword search misses RB-113. Vector search understands that RAM means memory.

Each search is right when the other is wrong. That is the reason to run both.
"""),
code('''
# --- Self-check: Section 2 (these check the data, so they pass without any code from you)
check("keyword search puts RB-113 first for the exact word OOMKilled",
      lambda: kit.runbook_of(bm25.search("OOMKilled at month end", k=1)[0]) == "RB-113")
check("vector search does not",
      lambda: kit.runbook_of(kit.vector_search(col, "OOMKilled at month end", k=1)[0]) != "RB-113")
check("vector search puts RB-113 first for 'too much RAM'",
      lambda: kit.runbook_of(kit.vector_search(col, "app killed because it used too much RAM", k=1)[0]) == "RB-113")
check("keyword search does not have RB-113 in its top 3",
      lambda: "RB-113" not in [kit.runbook_of(i) for i in bm25.search("app killed because it used too much RAM", k=3)])
'''),

md("""
## Section 3 &mdash; Merge the two lists with RRF

The two searches give scores on different scales, so you cannot just add them. **Reciprocal rank
fusion (RRF)** uses only the **rank**. A chunk at rank *r* in a list gets `1 / (c + r)` points
from that list, and its points from all lists are added. `c` is usually 60. It stops the first
place from counting too much.

A chunk that is near the top of **both** lists gets the most points.

Fill the two `BLANK`s: the points for one rank, and the sort order (highest total first).
"""),
code('''
def rrf(ranked_lists: list[list[str]], c: int = 60) -> list[str]:
    """Merge ranked lists of chunk ids into one list, best first."""
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0) + «1 / (c + rank)»
    return sorted(scores, key=lambda cid: «-scores[cid]»)


def hybrid_search(question: str, k: int = 5) -> list[str]:
    """Take 20 from each search, merge them, keep the best k."""
    return rrf([kit.vector_search(col, question, k=20), bm25.search(question, k=20)])[:k]


print(rrf([["a", "b", "c"], ["c", "a", "d"]]))
print(hybrid_search("OOMKilled at month end", k=3))
print(hybrid_search("app killed because it used too much RAM", k=3))
'''),
code('''
# --- Self-check: Section 3
check("rrf puts the chunk that is high in both lists first",
      lambda: rrf([["a", "b", "c"], ["c", "a", "d"]])[0] == "a")
check("rrf keeps every chunk from every list",
      lambda: sorted(rrf([["a", "b"], ["c"]])) == ["a", "b", "c"])
check("hybrid finds RB-113 in the top 2 for the exact word",
      lambda: "RB-113" in [kit.runbook_of(i) for i in hybrid_search("OOMKilled at month end", k=2)])
check("hybrid finds RB-113 in the top 2 for the meaning",
      lambda: "RB-113" in [kit.runbook_of(i) for i in hybrid_search("app killed because it used too much RAM", k=2)])
'''),

md("""
### Measure it on 14 questions

`data/questions.json` holds 14 on-call questions. For each one it names the **chunk** that holds
the answer, for example `RB-106#fix`. The cell below counts how often that chunk is in the top 3
for each search. This count is called **hit rate at 3**.
"""),
code('''
questions = kit.load_questions()

def hits_at_3(search) -> int:
    return sum(q["chunk"] in search(q["question"])[:3] for q in questions)

results = {
    "vector":  hits_at_3(lambda q: kit.vector_search(col, q, k=3)),
    "keyword": hits_at_3(lambda q: bm25.search(q, k=3)),
    "hybrid":  hits_at_3(lambda q: hybrid_search(q, k=3)),
}
for name, n in results.items():
    print(f"{name:8} {n:2}/{len(questions)}  " + "#" * n)
'''),
code('''
# --- Self-check: the measurement
check("hybrid is at least as good as the better single search",
      lambda: results["hybrid"] >= max(results["vector"], results["keyword"]))
check("and strictly better than each one on its own",
      lambda: results["hybrid"] > results["vector"] and results["hybrid"] > results["keyword"])
score()
'''),
md("""
## Your turn (if you have time)

1. Change `c` in `rrf` to 1 and then to 200. Run the measurement again. What happens to the
   hybrid count, and why?
2. Look at the questions that hybrid still misses:
   `[q["chunk"] for q in questions if q["chunk"] not in hybrid_search(q["question"], k=3)]`.
   Which chunk comes first instead? Is it a wrong answer, or the right runbook but the wrong section?
3. Lab R.2 takes the top **20** of your hybrid search and asks a **reranker** to choose the best 3.
   Keep this notebook open. You will compare against the hybrid count you just measured.
"""),
]

if __name__ == "__main__":
    write("lab-r1-hybrid-retrieval.ipynb", cells)
