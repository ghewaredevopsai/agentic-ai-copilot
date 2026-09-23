from nbgen import SETUP, code, md, write

cells = [
md("""
# Lab R.4 &mdash; Evaluation with Ragas

**Day 2 &middot; Module 3 &mdash; RAG, Vector Stores & Agent Memory** &nbsp;|&nbsp; **Time:** about 30 min

You have built a RAG pipeline in parts: hybrid search (R.1), a reranker (R.2) and an answer step.
Now you measure it with **Ragas**, an open-source library that scores RAG pipelines. It uses an
LLM as the judge, here the sandbox model.

Ragas gives four scores between 0 and 1. Two check **retrieval** and two check the **answer**:

| Metric | Stage | The question it answers |
|---|---|---|
| **context precision** | retrieval | Are the chunks we retrieved relevant, with the useful ones near the top? |
| **context recall** | retrieval | Do the chunks contain everything the reference answer needs? |
| **faithfulness** | answer | Is every claim in the answer backed by the chunks? |
| **answer relevancy** | answer | Does the answer address the question that was asked? |

You score the pipeline twice: once with hybrid search only, and once with the LLM reranker from
Lab R.2. Then you decide which stage is the weak one.

> **How this lab works.** Replace every `BLANK`, then run the **Self-check** cell below it. A cell
> that uses an empty `BLANK` stops with `NameError: name 'BLANK' is not defined`. That is expected.
> Each Ragas run makes about 40 calls to the sandbox model and takes a few minutes. Start it,
> then read the next section while it runs.
"""),
code(SETUP),

md("""
## Section 0 &mdash; Install Ragas

Ragas is not in the sandbox image, so install it now. The version is pinned, so everyone gets
the same one.
"""),
code('''
%pip install -q "ragas==0.4.3"

import site
site.addsitedir(site.getusersitepackages())   # use the new package without a kernel restart
'''),
md("""
Ragas 0.4.3 imports a Google Vertex AI class from `langchain_community` at start-up, and the
newer `langchain_community` in this sandbox no longer has that module. This lab does not use
Vertex AI, so the cell below puts an empty stand-in module in its place before Ragas is
imported. It is a known workaround and it changes nothing else.
"""),
code('''
import types
_stub = types.ModuleType("langchain_community.chat_models.vertexai")
_stub.ChatVertexAI = type("ChatVertexAI", (), {})
sys.modules.setdefault("langchain_community.chat_models.vertexai", _stub)

import ragas
from ragas import evaluate, EvaluationDataset, RunConfig
from ragas.metrics import (Faithfulness, ResponseRelevancy,
                           LLMContextPrecisionWithReference, LLMContextRecall)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_core.embeddings import Embeddings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

class LocalEmbeddings(Embeddings):
    """The same all-MiniLM-L6-v2 that Chroma uses, so no model download and no gateway call."""
    def __init__(self):
        self.fn = DefaultEmbeddingFunction()
    def embed_documents(self, texts):
        return [[float(x) for x in v] for v in self.fn(texts)]
    def embed_query(self, text):
        return self.embed_documents([text])[0]

judge = LangchainLLMWrapper(ChatOpenAI(model=os.environ["LAB_LLM_MODEL"], temperature=0,
                                       extra_body=kit.NO_THINK))
embeddings = LangchainEmbeddingsWrapper(LocalEmbeddings())
METRICS = [LLMContextPrecisionWithReference(), LLMContextRecall(), Faithfulness(), ResponseRelevancy()]
print("Ragas", ragas.__version__, "| judge:", os.environ["LAB_LLM_MODEL"])
'''),

md("""
## Section 1 &mdash; The pipeline under test

This cell is given. It rebuilds your hybrid search from Lab R.1 and the LLM reranker from Lab R.2,
and adds the **answer step**: the top 3 chunks go into a prompt that tells the model to answer
only from them.

The evaluation uses **6 of the 14 questions**: the ones where hybrid search did **not** put the
answer chunk in its top 3. A good test set contains the hard cases, not only the easy ones.
"""),
code('''
import re, time

chunks = kit.all_chunks()
text = {c["id"]: c["text"] for c in chunks}
col = kit.build_collection(chunks)
bm25 = kit.BM25(chunks)

def rrf(ranked_lists, c=60):
    scores = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (c + rank)
    return sorted(scores, key=lambda cid: -scores[cid])

def candidates(question, n=20):
    return rrf([kit.vector_search(col, question, k=20), bm25.search(question, k=20)])[:n]

def llm_rerank(question, ids):
    numbered = "\\n".join(f"[{n}] {text[cid]}" for n, cid in enumerate(ids))
    reply, _ = kit.chat(f"Question: {question}\\n\\nPassages:\\n{numbered}\\n\\n"
                        "Which 3 passages best answer the question? "
                        "Reply with their numbers only, best first, like: 4, 0, 7", max_tokens=20)
    picked = []
    for n in map(int, re.findall(r"\\d+", reply)):
        if n < len(ids) and ids[n] not in picked:
            picked.append(ids[n])
    return picked + [cid for cid in ids if cid not in picked]

def retrieve(question, rerank=False):
    ids = candidates(question)
    ids = llm_rerank(question, ids) if rerank else ids
    return [text[cid] for cid in ids[:3]]

def answer(question, contexts):
    passages = "\\n\\n".join(contexts)
    reply, _ = kit.chat("Answer the on-call engineer's question using ONLY the runbook passages below. "
                        "If they do not contain the answer, say so. Answer in at most 3 sentences.\\n\\n"
                        f"Passages:\\n{passages}\\n\\nQuestion: {question}", max_tokens=200)
    return reply.strip()

all_q = kit.load_questions()
eval_questions = [q for q in all_q if q["chunk"] not in candidates(q["question"])[:3]][:6]
for q in eval_questions:
    print("-", q["question"])
'''),

md("""
## Section 2 &mdash; Build the evaluation set

Ragas needs four things for each question. Fill the two `BLANK`s:

- `user_input`: the question;
- `retrieved_contexts`: the list of chunk texts that retrieval returned;
- `response`: the pipeline's answer;
- `reference`: the correct answer, written by a person. It is in `q["reference"]`.
"""),
code('''
def build_samples(rerank: bool) -> list[dict]:
    samples = []
    for q in eval_questions:
        contexts = retrieve(q["question"], rerank=rerank)
        samples.append({
            "user_input": q["question"],
            "retrieved_contexts": «contexts»,
            "response": answer(q["question"], contexts),
            "reference": «q["reference"]»,
        })
    return samples

samples_hybrid = build_samples(rerank=False)
print(samples_hybrid[0]["user_input"])
print("->", samples_hybrid[0]["response"])
'''),
code('''
# --- Self-check: Section 2
check("one sample per evaluation question",
      lambda: len(samples_hybrid) == len(eval_questions) == 6)
check("retrieved_contexts is a list of 3 chunk texts",
      lambda: all(isinstance(s["retrieved_contexts"], list) and len(s["retrieved_contexts"]) == 3
                  for s in samples_hybrid))
check("reference is the person-written answer, not the model's",
      lambda: samples_hybrid[0]["reference"] == eval_questions[0]["reference"])
'''),

md("""
## Section 3 &mdash; Score it, twice

The cell below scores the hybrid-only pipeline, then builds a second set **with** the LLM
reranker and scores that. It takes a few minutes. While it runs, predict: which of the four
scores should the reranker change most, and which should it hardly change?
"""),
code('''
def score_samples(samples):
    result = evaluate(EvaluationDataset.from_list(samples), metrics=METRICS, llm=judge,
                      embeddings=embeddings, show_progress=False,
                      run_config=RunConfig(timeout=300, max_workers=4))
    return result.to_pandas()

t0 = time.time()
table_hybrid = score_samples(samples_hybrid)
samples_rerank = build_samples(rerank=True)
table_rerank = score_samples(samples_rerank)
print(f"done in {time.time() - t0:.0f} s")

NAMES = ["llm_context_precision_with_reference", "context_recall", "faithfulness", "answer_relevancy"]
means = {"hybrid": table_hybrid[NAMES].mean(), "hybrid + rerank": table_rerank[NAMES].mean()}
print(f"\\n{'metric':40}{'hybrid':>10}{'+ rerank':>10}")
for name in NAMES:
    print(f"{name:40}{means['hybrid'][name]:>10.2f}{means['hybrid + rerank'][name]:>10.2f}")
'''),

md("""
## Section 4 &mdash; Which stage is weak?

A low **retrieval** score means the right text never reached the model: fix chunking, search or
reranking. A low **answer** score with good retrieval means the model had the text and still
answered badly: fix the prompt or the model.

Write `weakest_stage()`. It returns `"retrieval"` when the average of the two retrieval metrics is
lower than the average of the two answer metrics, and `"answer"` otherwise.
"""),
code('''
RETRIEVAL = ["llm_context_precision_with_reference", "context_recall"]
ANSWER = ["faithfulness", "answer_relevancy"]

def weakest_stage(m) -> str:
    retrieval = sum(m[n] for n in RETRIEVAL) / 2
    answer_ = sum(m[n] for n in ANSWER) / 2
    return «"retrieval" if retrieval < answer_ else "answer"»

for name, m in means.items():
    print(f"{name:16} weakest stage: {weakest_stage(m)}")
'''),
code('''
# --- Self-check: Sections 3 and 4
import math
check("every metric produced a score for both runs",
      lambda: all(not math.isnan(m[n]) for m in means.values() for n in NAMES),
      "a NaN usually means the judge's reply could not be read: run Section 3 again")
check("all scores are between 0 and 1",
      lambda: all(0 <= m[n] <= 1 for m in means.values() for n in NAMES))
check("weakest_stage reads the retrieval scores",
      lambda: weakest_stage({"llm_context_precision_with_reference": 0.1, "context_recall": 0.2,
                             "faithfulness": 0.9, "answer_relevancy": 0.9}) == "retrieval")
check("and the answer scores",
      lambda: weakest_stage({"llm_context_precision_with_reference": 0.9, "context_recall": 0.9,
                             "faithfulness": 0.3, "answer_relevancy": 0.8}) == "answer")
score()
'''),

md("""
## Your turn

1. Compare the two runs. Which metric moved most with the reranker? Was your prediction right?
2. Find the question with the lowest **faithfulness** in `table_hybrid`. Read its `response` and
   its `retrieved_contexts`. What did the model add that the chunks did not say?
3. Ragas uses an LLM as the judge, so its scores vary a little between runs. Run Section 3 again.
   How big is that change compared with the change the reranker made? A change is only real
   when it is bigger than this noise.
4. Keep these 6 questions and their references. Re-run this notebook every time you change the
   pipeline (chunk size, `c` in RRF, the reranker, the answer prompt), and keep a change only
   when the scores go up.
"""),
]

if __name__ == "__main__":
    write("lab-r4-ragas-evaluation.ipynb", cells)
