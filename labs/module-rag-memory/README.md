# RAG, vector stores and agent memory — Labs R.1 to R.4

**Day 2 · Module 3** · four labs · about 2 hours in total · runs in the **sandbox JupyterLab** ·
Folder: `labs/module-rag-memory/` in this course folder

In Module 3, AskOps searched runbooks by the words in their titles. In these labs you replace that
search with retrieval over the full runbook text. Then you measure it, and you give the agent a
memory that lasts across sessions.

| Lab | Notebook | After the slide | Time | Calls the model? |
|---|---|---|---|---|
| **R.1** Hybrid retrieval | `lab-r1-hybrid-retrieval.ipynb` | Hybrid retrieval | 25 min | no |
| **R.2** Rerankers | `lab-r2-rerankers.ipynb` | Rerankers | 30 min | yes, about 15 calls |
| **R.3** Long-term memory | `lab-r3-memory-policies.ipynb` | Long-term memory | 25 min | no |
| **R.4** Evaluation with Ragas | `lab-r4-ragas-evaluation.ipynb` | Evaluation with Ragas | 30 min | yes, about 100 calls |

## Words used in these labs

The deck's *Words used in this module* slide has the words from the deck. The ones you need most:

- **Chunk:** one piece of a document. Here, one section of a runbook: *Symptoms*, *Checks*, *Fix*
  or *Escalation*.
- **Metadata:** labels stored next to a chunk, such as `service` and `access`. You can filter on them.
- **Hit rate at 3:** how many questions have the chunk with the answer in the top 3 results.
- **Reranker:** a second stage that reads the question and each chunk together, and picks the best few.
- **Judge:** the LLM that Ragas uses to score answers. Here it is the sandbox model.

## Before you start

Open the sandbox JupyterLab. In the file browser, go to this course folder, then
`labs/module-rag-memory/`. You should see:

```text
data/                          runbooks/ (13 runbooks) and questions.json (14 questions)
rag_kit.py                     the shared helpers: split, embed, search, chat
lab-r1-hybrid-retrieval.ipynb  ... lab-r4-ragas-evaluation.ipynb
solutions/                     one answer to every lab
```

The sandbox already knows where its model is, so there is nothing to configure. Run the **Setup**
cell at the top of each notebook first. It prints the number of chunks, which is **52**.

**Do not open `solutions/` until you have tried the lab.**

## How each notebook works

- Replace every `BLANK` with your code, then run the **Self-check** cell below it.
- A check prints `[PASS]`, `[FAIL]` or `[TODO]`. `[TODO]` means a `BLANK` is still there, or a cell
  above it has not run yet.
- A cell that uses an empty `BLANK` stops with `NameError: name 'BLANK' is not defined`. That is
  expected. Fill the `BLANK` and run the cell again.
- The last cell prints `Score: passed/total`. It is feedback for you, not a grade.

## Lab R.1 — Hybrid retrieval

**Goal:** see keyword search and vector search fail on different questions, and merge them.

1. **Chunks and metadata.** Read one chunk and its metadata. Write two `where` filters. One keeps a
   search inside the ledger service. The other keeps out the restricted runbook, RB-111.
2. **Two searches that disagree.** Run *"OOMKilled at month end"* and *"app killed because it used
   too much RAM"* through both searches. Each search finds RB-113 for one question and misses it
   for the other.
3. **RRF.** Write the reciprocal rank fusion merge. Then measure hit rate at 3 on the 14 questions
   for vector, keyword and hybrid search.

## Lab R.2 — Rerankers

**Goal:** decide whether a reranker earns its cost, with numbers.

1. **Baseline.** Measure hybrid search at 1 and at 3.
2. **Cross-encoder.** Rerank the top 20 with a small cross-encoder model, and measure again. The
   first run downloads the model, about 90 MB.
3. **LLM as reranker.** Send the 20 chunks to the sandbox model in one prompt, and ask for the best
   3. Measure again, and count the tokens.
4. **Compare.** Put the three rows side by side, and answer the questions in the notebook.

## Lab R.3 — Long-term memory

**Goal:** write the rules that decide what an agent remembers, and for how long.

1. **Write policy.** Refuse guesses, unconfirmed facts, secrets and card numbers.
2. **Replace and evict.** A newer fact with the same key replaces the old one. Items expire after a
   time to live (TTL), and a size cap removes the least recently used items.
3. **A month of sessions.** Simulate days 1 to 45, and check what the store holds.
4. **The cap, and forgetting.** Add eight facts to a store of six, and then delete a memory on request.

## Lab R.4 — Evaluation with Ragas

**Goal:** score the whole pipeline, and find its weakest stage.

0. **Install Ragas.** The first cell installs a pinned version. The next cell adds a small
   workaround for one import that Ragas needs, and the notebook explains it.
1. **The pipeline.** Hybrid search, the LLM reranker and an answer step, all given. The test set is
   the 6 questions where hybrid search missed.
2. **The evaluation set.** Fill in what Ragas needs for each question.
3. **Score twice.** Score without the reranker, then with it. This takes a few minutes.
4. **Weakest stage.** Decide whether retrieval or the answer step needs the next fix.

## What you take away

- Keyword search and vector search fail on different questions. Hybrid search runs both and merges
  them by rank.
- Metadata filters decide what a search may return, including who may see what.
- A reranker is a second stage, applied to about 20 chunks. Measure it on your own questions before
  you keep it.
- Long-term memory needs a write policy and an eviction policy, written as code.
- Ragas separates retrieval scores from answer scores, so you know which stage to fix next.
  A change is real only when it is bigger than the judge's noise.

---
*Gheware DevOps & Agentic AI · [devops.gheware.com](https://devops.gheware.com)*
