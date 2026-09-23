from nbgen import SETUP, code, md, write

cells = [
md("""
# Lab R.2 &mdash; Rerankers: search wide, then read closely

**Day 2 &middot; Module 3 &mdash; RAG, Vector Stores & Agent Memory** &nbsp;|&nbsp; **Time:** about 30 min

In Lab R.1, hybrid search put the right chunk in the top 3 for some of the 14 questions, but not
all. Here you keep the **top 20** from hybrid search and add a second stage, a **reranker**, that
reads each question and chunk together and chooses the best 3.

You try two rerankers on the same 20 candidates:

1. a **cross-encoder**: a small model built only for scoring (question, chunk) pairs;
2. **the LLM itself**, asked to pick the 3 chunks that best answer the question.

For each one you measure **hit rate at 3** (the answer chunk is in the top 3), **hit rate at 1**,
the time taken and, for the LLM, the tokens used. Then you decide if the reranker earns its cost.

> **How this lab works.** Replace every `BLANK`, then run the **Self-check** cell below it. A cell
> that uses an empty `BLANK` stops with `NameError: name 'BLANK' is not defined`. That is expected.
> Section 2 downloads a small model (about 90 MB) the first time. Section 3 calls the sandbox
> model 14 times, about 1,000 tokens each.
"""),
code(SETUP),

md("""
## Section 1 &mdash; The baseline: hybrid search from Lab R.1

This is the `rrf` and `hybrid_search` you wrote in Lab R.1. `candidates()` returns the top 20
chunk ids for a question. `measure()` counts hits at 1 and at 3 for any ranking function.
Run it and note the baseline numbers.
"""),
code('''
import time

chunks = kit.all_chunks()
text = {c["id"]: c["text"] for c in chunks}
col = kit.build_collection(chunks)
bm25 = kit.BM25(chunks)
questions = kit.load_questions()

def rrf(ranked_lists, c=60):
    scores = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (c + rank)
    return sorted(scores, key=lambda cid: -scores[cid])

def candidates(question: str, n: int = 20) -> list[str]:
    return rrf([kit.vector_search(col, question, k=20), bm25.search(question, k=20)])[:n]

def measure(name: str, rank_fn) -> dict:
    """rank_fn(question, candidate_ids) -> the same ids in a new order, best first."""
    t0, at1, at3 = time.time(), 0, 0
    for q in questions:
        ranked = rank_fn(q["question"], candidates(q["question"]))
        at1 += ranked[:1] == [q["chunk"]]
        at3 += q["chunk"] in ranked[:3]
    row = {"method": name, "hit@1": at1, "hit@3": at3, "seconds": round(time.time() - t0, 1)}
    print(row)
    return row

baseline = measure("hybrid only", lambda question, ids: ids)
'''),

md("""
## Section 2 &mdash; A cross-encoder reranker

A **cross-encoder** reads the question and one chunk **together**, as one input, and returns a
relevance score. Hybrid search could not do that: each chunk's vector was made in advance,
before anyone asked the question.

`cross-encoder/ms-marco-MiniLM-L-6-v2` is a popular small reranker. It was trained on web
search questions (the MS MARCO data set). Fill the two `BLANK`s: the pairs to score, and the
sort order (highest score first).
"""),
code('''
from sentence_transformers import CrossEncoder

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")   # downloads once

def cross_encoder_rerank(question: str, ids: list[str]) -> list[str]:
    pairs = [(question, «text[cid]») for cid in ids]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(scores, ids), key=«lambda pair: -pair[0]»)
    return [cid for _, cid in ranked]

q0 = questions[5]["question"]
print(q0)
print("hybrid  :", candidates(q0)[:3])
print("reranked:", cross_encoder_rerank(q0, candidates(q0))[:3])
'''),
code('''
# --- Self-check: Section 2
_ids = candidates(questions[0]["question"])
check("the reranker returns the same 20 ids, in a new order",
      lambda: sorted(cross_encoder_rerank(questions[0]["question"], _ids)) == sorted(_ids))
check("the best-scored chunk comes first",
      lambda: cross_encoder_rerank("Customers get HTTP 413 when they upload a photo",
                                   candidates("Customers get HTTP 413 when they upload a photo"))[0].startswith("RB-110"))
'''),
code('''
ce_row = measure("cross-encoder", cross_encoder_rerank)
print("\\nbaseline was:", baseline)
'''),
md("""
**Read your numbers.** Did the cross-encoder beat hybrid search at 3? On these runbooks it usually
does **not** do much better. It learned what a good answer to a *web search* looks like, and an
on-call runbook reads differently. A reranker is not magic. You only know it helps when you
measure it on **your** questions.
"""),

md("""
## Section 3 &mdash; The LLM as a reranker

A larger model understands the question much better. So you can send it the 20 candidates in
**one** prompt, numbered 0 to 19, and ask for the numbers of the best 3. This is called
**listwise** reranking. It costs one model call per question.

The prompt is given. Fill the `BLANK`: turn the numbers in the reply into chunk ids. Ignore any
number that is not a valid position. The rest of the list stays in hybrid order after the picks.
"""),
code('''
import re

llm_tokens = 0

def llm_rerank(question: str, ids: list[str]) -> list[str]:
    global llm_tokens
    numbered = "\\n".join(f"[{n}] {text[cid]}" for n, cid in enumerate(ids))
    prompt = (f"Question: {question}\\n\\nPassages:\\n{numbered}\\n\\n"
              "Which 3 passages best answer the question? "
              "Reply with their numbers only, best first, like: 4, 0, 7")
    reply, tokens = kit.chat(prompt, max_tokens=20)
    llm_tokens += tokens
    numbers = [int(n) for n in re.findall(r"\\d+", reply)]
    picked = []
    for n in numbers:
        if «n < len(ids)» and ids[n] not in picked:
            picked.append(ids[n])
    return picked + [cid for cid in ids if cid not in picked]

print(q0)
print("llm reranked:", llm_rerank(q0, candidates(q0))[:3], f"({llm_tokens} tokens)")
'''),
code('''
# --- Self-check: Section 3 (the first check calls the model once)
_ids = candidates(questions[0]["question"])
check("the LLM reranker returns the same 20 ids, in a new order",
      lambda: sorted(llm_rerank(questions[0]["question"], _ids)) == sorted(_ids))
'''),
code('''
llm_tokens = 0
llm_row = measure("LLM rerank", llm_rerank)
llm_row["tokens"] = llm_tokens
print(f"\\n{llm_tokens} tokens for {len(questions)} questions, "
      f"about {llm_tokens // len(questions)} per question")
'''),
code('''
# --- Self-check: the measurement
check("the LLM reranker is at least as good as hybrid at 3",
      lambda: llm_row["hit@3"] >= baseline["hit@3"])
check("and better than hybrid at 1",
      lambda: llm_row["hit@1"] > baseline["hit@1"],
      "look at a question it got wrong: did the reply contain three numbers?")
score()
'''),

md("""
## Section 4 &mdash; Does it earn its cost?

Put the three rows side by side.
"""),
code('''
rows = [baseline, ce_row, llm_row]
print(f"{'method':15}{'hit@1':>7}{'hit@3':>7}{'seconds':>9}{'tokens':>8}")
for r in rows:
    print(f"{r['method']:15}{r['hit@1']:>7}{r['hit@3']:>7}{r['seconds']:>9}{r.get('tokens', 0):>8}")
'''),
md("""
Think about these questions, and write your answers in your notes:

1. The LLM reranker used about 1,000 tokens per question. If it lets you send **3** chunks to the
   answer step instead of **10**, how many tokens does that save in the answer prompt? Does the
   reranker pay for itself?
2. Which is faster per question here, the cross-encoder or the LLM? Which would you choose for
   an agent that searches 5 times in one run?
3. The cross-encoder did not help much on these runbooks. Name one way you could still make a
   small, fast reranker work for your documents.

In Lab R.4 you measure the **answers**, not only the chunks, and you can check whether the
reranker improves them.
"""),
]

if __name__ == "__main__":
    write("lab-r2-rerankers.ipynb", cells)
