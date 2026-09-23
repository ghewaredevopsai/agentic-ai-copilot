"""Shared helpers for the RAG and memory labs (R.1 to R.4).

The notebooks import it, so each lab shows only what is new. You can read it; you do not edit it.

    load_runbooks()      read data/runbooks/*.md into dicts
    split_runbook()      one chunk per "## " section, each with metadata
    all_chunks()         every chunk of every runbook
    build_collection()   a Chroma collection of those chunks (in memory)
    vector_search()      search the collection by meaning
    BM25                 keyword search, the classic formula, in plain Python
    chat()               one call to the sandbox model, with its token count
"""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNBOOK_DIR = HERE / "data" / "runbooks"
QUESTIONS_FILE = HERE / "data" / "questions.json"


# ---------------------------------------------------------------- load and split
def load_runbooks(folder: Path = RUNBOOK_DIR) -> list[dict]:
    """Each runbook is a Markdown file with a small header between two '---' lines."""
    books = []
    for path in sorted(folder.glob("RB-*.md")):
        text = path.read_text(encoding="utf-8")
        _, header, body = text.split("---", 2)
        meta = dict(line.split(": ", 1) for line in header.strip().splitlines())
        books.append({**meta, "body": body.strip()})
    return books


def split_runbook(book: dict) -> list[dict]:
    """Split on '## ' headings: one chunk per section.

    Every chunk starts with the runbook id and title. Without that line, a chunk that
    says only "Restart one pod at a time" does not say which problem it fixes.
    """
    chunks = []
    for part in re.split(r"^## ", book["body"], flags=re.M)[1:]:
        section, _, text = part.partition("\n")
        chunks.append({
            "id": f"{book['id']}#{section.strip().lower()}",
            "text": f"{book['id']} {book['title']} - {section.strip()}: {text.strip()}",
            "metadata": {
                "runbook": book["id"],
                "title": book["title"],
                "section": section.strip(),
                "service": book["service"],
                "access": book["access"],
                "updated": book["updated"],
            },
        })
    return chunks


def all_chunks() -> list[dict]:
    return [c for book in load_runbooks() for c in split_runbook(book)]


def load_questions() -> list[dict]:
    """The lab question set: a question, the runbook that answers it, and a reference answer."""
    return json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- vector search
def build_collection(chunks: list[dict] | None = None, name: str = "runbooks"):
    """An in-memory Chroma collection. The embedding model is Chroma's default,
    all-MiniLM-L6-v2 (384 numbers per text), which is already in the sandbox."""
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    chunks = all_chunks() if chunks is None else chunks
    client = chromadb.Client()
    try:
        client.delete_collection(name)
    except Exception:
        pass
    col = client.create_collection(name, embedding_function=DefaultEmbeddingFunction(),
                                   metadata={"hnsw:space": "cosine"})
    col.add(ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks])
    return col


def vector_search(col, question: str, k: int = 5, where: dict | None = None) -> list[str]:
    """Chunk ids, closest meaning first."""
    res = col.query(query_texts=[question], n_results=k, **({"where": where} if where else {}))
    return res["ids"][0]


# ---------------------------------------------------------------- keyword search
def tokenize(text: str) -> list[str]:
    """Lower case, and keep codes such as ora-12541 or 502 as one word."""
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


class BM25:
    """Keyword search with the BM25 formula, the default in Elasticsearch and OpenSearch.

    A chunk scores high when it contains the question's words, when those words are rare
    across all chunks, and when the chunk is not very long.
    """

    def __init__(self, chunks: list[dict], k1: float = 1.5, b: float = 0.75):
        self.ids = [c["id"] for c in chunks]
        self.docs = [tokenize(c["text"]) for c in chunks]
        self.k1, self.b = k1, b
        self.avg_len = sum(map(len, self.docs)) / len(self.docs)
        n = len(self.docs)
        df: dict[str, int] = {}
        for doc in self.docs:
            for word in set(doc):
                df[word] = df.get(word, 0) + 1
        self.idf = {w: math.log(1 + (n - d + 0.5) / (d + 0.5)) for w, d in df.items()}

    def score(self, question: str, doc: list[str]) -> float:
        total = 0.0
        for word in tokenize(question):
            tf = doc.count(word)
            if tf:
                norm = tf + self.k1 * (1 - self.b + self.b * len(doc) / self.avg_len)
                total += self.idf[word] * tf * (self.k1 + 1) / norm
        return total

    def search(self, question: str, k: int = 5) -> list[str]:
        """Chunk ids, best keyword match first. Chunks that share no word are left out."""
        scored = [(self.score(question, d), i) for d, i in zip(self.docs, self.ids)]
        scored = [(s, i) for s, i in scored if s > 0]
        scored.sort(key=lambda p: (-p[0], p[1]))
        return [i for _, i in scored[:k]]


def runbook_of(chunk_id: str) -> str:
    """'RB-107#fix' -> 'RB-107'"""
    return chunk_id.split("#")[0]


# ---------------------------------------------------------------- the chat model
# The sandbox sets OPENAI_BASE_URL, OPENAI_API_KEY and LAB_LLM_MODEL, so there is nothing
# to configure. Thinking is switched off and temperature is 0, so runs can be compared.
NO_THINK = {"chat_template_kwargs": {"enable_thinking": False}}


def chat(prompt: str, max_tokens: int = 400) -> tuple[str, int]:
    """Send one user message. Returns (reply text, prompt tokens + completion tokens)."""
    from openai import OpenAI

    client = OpenAI()
    reply = client.chat.completions.create(
        model=os.environ["LAB_LLM_MODEL"], temperature=0, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}], extra_body=NO_THINK)
    return reply.choices[0].message.content or "", reply.usage.total_tokens
