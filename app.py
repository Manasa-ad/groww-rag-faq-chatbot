"""RAG-based Mutual Fund FAQ Chatbot — Groww Mutual Fund (facts-only, no advice).

Answers a fixed set of factual question types about 4 Groww Mutual Fund schemes
from a small corpus of official AMC/AMFI/SEBI pages, always with a citation.
Refuses opinion/advice questions and anything containing PII.
"""
import json
import pickle
import re
from datetime import date
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent

DISCLAIMER = "Facts-only. No investment advice."

EDUCATIONAL_LINK = "https://www.mutualfundssahihai.com/en/what-are-expenses-incurred-mutual-fund-scheme"
CORPUS_REFRESH_DATE = "2026-08-27"

SCHEME_ALIASES = {
    "Large Cap": ["large cap", "largecap", "large-cap"],
    "Multicap": ["multicap", "multi cap", "multi-cap", "flexi cap", "flexi-cap", "flexicap"],
    "ELSS Tax Saver": ["elss", "tax saver", "tax-saver", "tax saving"],
    "Liquid": ["liquid"],
}

FACT_ALIASES = {
    "expense_ratio": ["expense ratio", r"\bter\b", "total expense"],
    "exit_load": ["exit load", "exit fee", "exit charge"],
    "min_sip": ["min sip", "minimum sip", "min. sip", "minimum sip amount"],
    "min_lumpsum": ["min lumpsum", "minimum lumpsum", "min. lumpsum", "minimum investment", "minimum lump sum"],
    "lock_in": ["lock in", "lock-in", "lockin"],
    "riskometer": ["riskometer", "risk-o-meter", "risk o meter", "risk level", "how risky"],
    "benchmark": [r"\bbenchmark\b"],
}

FACT_LABELS = {
    "expense_ratio": "expense ratio",
    "exit_load": "exit load",
    "min_sip": "minimum SIP amount",
    "min_lumpsum": "minimum lumpsum amount",
    "lock_in": "lock-in period",
    "riskometer": "riskometer",
    "benchmark": "benchmark",
}

OPINION_PATTERNS = [
    r"\bshould i\b", r"\bshould we\b",
    r"\bbuy or sell\b", r"\bbuy vs sell\b",
    r"\bwhich (fund|scheme) is better\b", r"\bwhich is better\b",
    r"\bworth investing\b", r"\brecommend\b", r"\brecommendation\b",
    r"\bbest (fund|scheme)\b", r"\bgood investment\b", r"\bshould i invest\b",
    r"\bis it (a )?good time\b", r"\bwill (it|this) give (good |high )?returns\b",
    r"\bpredict\b", r"\bforecast\b", r"\bcompare returns?\b", r"\bwhich one to (buy|choose|pick)\b",
]

PII_PATTERNS = {
    "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "Aadhaar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "phone": re.compile(r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b"),
}

STATEMENT_KEYWORDS = ["capital gain", "statement", "cas", "tax document", "download"]


@st.cache_resource
def load_facts():
    with open(ROOT / "data" / "facts.json") as f:
        return json.load(f)


@st.cache_resource
def load_index():
    with open(ROOT / "data" / "chunks.pkl", "rb") as f:
        return pickle.load(f)


def detect_pii(query: str):
    hits = []
    for label, pattern in PII_PATTERNS.items():
        if pattern.search(query):
            hits.append(label)
    return hits


def detect_opinion(query: str) -> bool:
    q = query.lower()
    return any(re.search(pat, q) for pat in OPINION_PATTERNS)


def detect_scheme(query: str):
    q = query.lower()
    for scheme, aliases in SCHEME_ALIASES.items():
        if any(a in q for a in aliases):
            return scheme
    return None


def detect_fact_type(query: str):
    q = query.lower()
    for fact_key, aliases in FACT_ALIASES.items():
        if any(re.search(a, q) for a in aliases):
            return fact_key
    return None


def answer_from_facts(scheme: str, fact_key: str, facts: dict) -> str:
    row = facts[scheme]
    value = row.get(fact_key)
    label = FACT_LABELS[fact_key]
    if fact_key == "lock_in" and value is None:
        return (
            f"Groww {scheme} Fund does not have a lock-in period (only ELSS schemes do). "
            f"Source: {row['source_url']}\n\nLast updated from sources: {row['fetched_on']}"
        )
    if value is None:
        return (
            f"The {label} for Groww {scheme} Fund is not published on the official scheme page as of "
            f"{row['fetched_on']}. Source checked: {row['source_url']}\n\n"
            f"Last updated from sources: {row['fetched_on']}"
        )
    return (
        f"The {label} for Groww {scheme} Fund is **{value}**. Source: {row['source_url']}\n\n"
        f"Last updated from sources: {row['fetched_on']}"
    )


def retrieve_answer(query: str, index: dict, top_k: int = 1, min_score: float = 0.12):
    from sklearn.metrics.pairwise import cosine_similarity

    vec = index["vectorizer"].transform([query])
    sims = cosine_similarity(vec, index["matrix"])[0]
    top_idx = sims.argsort()[::-1][:top_k]
    results = [(index["chunks"][i], sims[i]) for i in top_idx if sims[i] >= min_score]
    return results


def summarize_chunk(text: str, query: str, vectorizer, max_sentences: int = 3) -> str:
    """Pick the sentences within the chunk most relevant to the query, rather than
    just the first N (a chunk's opening sentences aren't necessarily the ones that
    actually answer the question)."""
    from sklearn.metrics.pairwise import cosine_similarity

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if len(sentences) <= max_sentences:
        return " ".join(sentences)
    sent_vecs = vectorizer.transform(sentences)
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, sent_vecs)[0]
    top_idx = sorted(sims.argsort()[::-1][:max_sentences])  # keep original order among the picked ones
    return " ".join(sentences[i] for i in top_idx)


def route_query(query: str, facts: dict, index: dict) -> str:
    pii_hits = detect_pii(query)
    if pii_hits:
        return (
            "I can't process personal information like PAN, Aadhaar, phone numbers, or email addresses. "
            "Please don't share these here, they're not needed to answer factual scheme questions."
        )

    if detect_opinion(query):
        return (
            "I only answer factual questions about scheme details (expense ratio, exit load, minimum SIP, "
            "lock-in, riskometer, benchmark), I can't advise on what to buy, sell, or which fund is better. "
            f"For general investing education, see: {EDUCATIONAL_LINK}"
        )

    scheme = detect_scheme(query)
    fact_key = detect_fact_type(query)

    if scheme and fact_key:
        return answer_from_facts(scheme, fact_key, facts)

    if scheme and not fact_key:
        row = facts[scheme]
        return (
            f"I can tell you the expense ratio, exit load, minimum SIP, lock-in, riskometer, or benchmark for "
            f"Groww {scheme} Fund, which one would you like? Source: {row['source_url']}\n\n"
            f"Last updated from sources: {row['fetched_on']}"
        )

    if any(kw in query.lower() for kw in STATEMENT_KEYWORDS):
        results = retrieve_answer(query, index)
        if results:
            chunk, score = results[0]
            summary = summarize_chunk(chunk["text"], query, index["vectorizer"])
            return (
                f"{summary} Source: {chunk['url']}\n\n"
                f"Last updated from sources: {CORPUS_REFRESH_DATE}"
            )

    results = retrieve_answer(query, index)
    if results:
        chunk, score = results[0]
        summary = summarize_chunk(chunk["text"], query, index["vectorizer"])
        return (
            f"Based on the sources I have: {summary} Source: {chunk['url']}\n\n"
            f"Last updated from sources: {CORPUS_REFRESH_DATE}"
        )

    scheme_list = ", ".join(f"Groww {s} Fund" for s in facts.keys())
    return (
        "I don't have that fact in my current sources. I can answer expense ratio, exit load, minimum SIP, "
        f"lock-in, riskometer, or benchmark questions for: {scheme_list}, or general questions like "
        "\"how do I download my capital gains statement?\""
    )


# ---------------- UI ----------------

st.set_page_config(page_title="Groww MF FAQ Assistant", page_icon="📄")

st.title("Groww Mutual Fund FAQ Assistant")
st.caption(DISCLAIMER)
st.write(
    "Hi! I answer factual questions about **Groww Large Cap, Multicap, ELSS Tax Saver, and Liquid Fund** "
    "(Direct, Growth) using only official AMC/AMFI/SEBI sources. Every answer includes a source link."
)

example_questions = [
    "What is the expense ratio of Groww Large Cap Fund?",
    "What is the ELSS lock-in period?",
    "How do I download my capital gains statement?",
]

cols = st.columns(3)
example_clicked = None
for col, q in zip(cols, example_questions):
    if col.button(q, use_container_width=True):
        example_clicked = q

if "history" not in st.session_state:
    st.session_state.history = []

facts = load_facts()
index = load_index()

query = st.chat_input("Ask about expense ratio, exit load, min SIP, lock-in, riskometer, benchmark...")
if example_clicked:
    query = example_clicked

if query:
    answer = route_query(query, facts, index)
    st.session_state.history.append((query, answer))

for q, a in reversed(st.session_state.history):
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        st.markdown(a)

st.divider()
st.caption(DISCLAIMER)
