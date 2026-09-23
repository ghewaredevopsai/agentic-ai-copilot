# RAG, vector stores and agent memory — Labs R.1 to R.4

**Day 2** · four notebook labs · about 1 hour 45 minutes · in the browser sandbox

AskOps searched runbooks by the words in their titles. In these labs it searches the full runbook
text, measures how well it finds the answer, remembers facts across sessions, and scores the whole
pipeline. Every lab ends with a real result.

| Lab | Notebook | Time | The result |
|---|---|---|---|
| R.1 Hybrid retrieval | `lab-r1-hybrid-retrieval.ipynb` | 25 min | Hybrid search beats vector and keyword search on 14 questions, and the model answers from what it found |
| R.2 Rerankers | `lab-r2-rerankers.ipynb` | 25 min | One table: hits, time and tokens for no reranker, a cross-encoder and the LLM |
| R.3 Long-term memory | `lab-r3-memory-policies.ipynb` | 25 min | On day 60 the model answers from what memory kept, and says what it forgot |
| R.4 Evaluation with Ragas | `lab-r4-ragas-evaluation.ipynb` | 30 min | Four scores for two versions of the pipeline, and the stage to fix next |

## What is in this folder

| File | What it is |
|---|---|
| `data/runbooks/` | 13 runbooks, one Markdown file each, with metadata at the top |
| `data/questions.json` | 14 on-call questions, each with the chunk that answers it and a reference answer |
| `rag_kit.py` | Shared helpers: split, embed, keyword search, and one call to the model. You do not edit it |

## Before you start

Open the sandbox JupyterLab, and go to `labs/module-rag-memory/` in this course folder. Open a
notebook, use the **Python 3** kernel, and run the cells in order with **Shift + Enter**. Under each
cell, **You should see** says what to expect. There is nothing to fill in and nothing is graded.

The sandbox already has everything these labs use: the model, the embedding model, the reranker
model and Ragas. Nothing is downloaded.

R.2 calls the model about 15 times, and R.4 about 100 times. The model's words change from run to
run. The numbers should stay close.

## Words used in these labs

- **Chunk:** one section of a runbook: *Symptoms*, *Checks*, *Fix* or *Escalation*.
- **Metadata:** labels stored next to a chunk, such as `service` and `access`. You can filter on them.
- **Hit rate at 3:** how many questions have the answer chunk in the top 3 results.
- **Reranker:** a second stage that reads the question and each chunk together, and picks the best few.
- **Ragas:** an open-source library that scores a RAG pipeline: two scores for retrieval, two for
  the answer.
- **Judge:** the model Ragas uses to score answers. Here it is the sandbox model.

## If something goes wrong

- **A model call fails or times out:** run the cell again.
- **`NameError`:** a cell above did not run. Use **Run** &rarr; **Run All Cells**.
- **R.4 prints `nan` for a score:** the judge's reply could not be read. Run Step 4 again.

## What you take away

- Keyword search and vector search fail on different questions. Hybrid search runs both and merges
  them by rank.
- Metadata filters decide what a search may return, including who may see what.
- A reranker is a second stage on about 20 chunks. Keep it only if it helps on your own questions.
- Long-term memory needs written rules: what may be saved, what replaces what, and what is evicted.
- Ragas scores retrieval and the answer separately, so you know which stage to fix. A change is real
  only when it is bigger than the judge's noise.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
