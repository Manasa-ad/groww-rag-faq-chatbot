"""Chunk every fetched raw text file and build a TF-IDF retrieval index.

Small corpus (~19 fetched docs), so a brute-force TF-IDF + cosine-similarity
index (scikit-learn) is used instead of a heavier embedding model — lighter to
install, faster to deploy on Streamlit Community Cloud's free tier, and lexical
matching suits this corpus well since the queries use precise domain terms
("expense ratio", "exit load", "riskometer") that appear near-verbatim in the
source pages.
"""
import pickle
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sources_data import SOURCES

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "data" / "raw"

CHUNK_WORDS = 220
CHUNK_OVERLAP_SENTENCES = 1

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str):
    # raw scraped text is line-broken, not sentence-broken; normalize to spaces first
    flat = " ".join(text.split())
    return [s.strip() for s in _SENTENCE_SPLIT.split(flat) if s.strip()]


def chunk_text(text: str, chunk_words: int = CHUNK_WORDS, overlap_sentences: int = CHUNK_OVERLAP_SENTENCES):
    """Accumulate whole sentences into ~chunk_words-sized chunks so a chunk never
    starts or ends mid-sentence (important for clean answer extraction later)."""
    sentences = split_sentences(text)
    if not sentences:
        return []
    chunks = []
    current = []
    current_words = 0
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        sent_words = len(sent.split())
        if current and current_words + sent_words > chunk_words:
            chunks.append(" ".join(current))
            current = current[-overlap_sentences:] if overlap_sentences else []
            current_words = sum(len(s.split()) for s in current)
        current.append(sent)
        current_words += sent_words
        i += 1
    if current:
        chunks.append(" ".join(current))
    return chunks


def main():
    src_by_id = {s["id"]: s for s in SOURCES}
    all_chunks = []  # list of {"text":..., "source_id":..., "url":..., "scheme":..., "category":...}

    for txt_path in sorted(RAW_DIR.glob("*.txt")):
        src_id = txt_path.stem
        src = src_by_id.get(src_id)
        if not src:
            continue
        text = txt_path.read_text(encoding="utf-8")
        for chunk in chunk_text(text):
            all_chunks.append(
                {
                    "text": chunk,
                    "source_id": src_id,
                    "url": src["url"],
                    "scheme": src["scheme"],
                    "category": src["category"],
                }
            )

    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_df=0.9,
        min_df=1,
    )
    matrix = vectorizer.fit_transform([c["text"] for c in all_chunks])

    with open(ROOT / "data" / "chunks.pkl", "wb") as f:
        pickle.dump(
            {
                "chunks": all_chunks,
                "vectorizer": vectorizer,
                "matrix": matrix,
            },
            f,
        )

    print(f"Indexed {len(all_chunks)} chunks from {len(set(c['source_id'] for c in all_chunks))} documents.")


if __name__ == "__main__":
    main()
