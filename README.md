# Groww Mutual Fund FAQ Assistant

A small, facts-only RAG chatbot for Groww Mutual Fund scheme questions (expense ratio, exit load, minimum SIP, ELSS lock-in, riskometer, benchmark, and how to download a capital-gains statement). Every answer cites the exact official source it came from. No investment advice, no PII handling.

## Scope

**AMC:** Groww Mutual Fund (growwmf.in — formerly Indiabulls Asset Management, rebranded ~2023 after Groww's acquisition)

**Schemes (4):**
- Groww Large Cap Fund (Direct, Growth)
- Groww Multicap Fund (Direct, Growth) — used as the flexi-cap-style diversified-equity slot; Groww MF has no dedicated Flexi Cap fund
- Groww ELSS Tax Saver Fund (Direct, Growth)
- Groww Liquid Fund (Direct, Growth)

**Corpus:** 25 official AMC/AMFI/SEBI URLs (`sources.md`), 19 fetched successfully into the working corpus (see Known Limits).

## Architecture

```
sources_data.py (the 25 URLs)
        │
        ▼
fetch_sources.py ──▶ data/raw/*.txt (scraped/parsed text) + data/fetch_log.json
        │
        ├──▶ build_facts.py ──▶ data/facts.json   (hand-verified structured facts per scheme,
        │                                           each with its own source URL + fetch date)
        │
        └──▶ build_index.py ──▶ data/chunks.pkl   (sentence-aware chunks, TF-IDF vectorized
                                                     with scikit-learn — no paid API, no GPU needed)
                │
                ▼
           app.py (Streamlit)
             1. Guardrails (regex, run first): PII detection → hard refuse;
                opinion/advice detection → polite refuse + educational link
             2. Fact router: scheme + fact-type both matched → answer straight from
                facts.json (deterministic, zero hallucination risk on the 6 canonical
                fact types); open-ended query → TF-IDF retrieval over chunks.pkl,
                best-matching sentences extracted as the answer
             3. UI: welcome line, 3 example questions, disclaimer, chat history,
                every answer carries its citation link
```

**Why no live LLM call:** this build deliberately avoids a live LLM API call. It uses
structured-fact lookup + TF-IDF retrieval + templated natural-language generation
instead. Reasoning: (1) no paid API was in scope for this build, (2) a local LLM's
cold-start and per-query latency is a real reliability risk on Streamlit Community
Cloud's free tier (no GPU, limited RAM) for a graded live demo, (3) the six canonical
fact types demand zero-hallucination accuracy, which a structured lookup guarantees
and a generative model doesn't. The "prompting skill" is demonstrated in how the
answer templates, refusal wording, and citation format are written, not in a live
model call.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/fetch_sources.py   # scrape/parse all sources → data/raw/, data/fetch_log.json
python scripts/build_facts.py     # write data/facts.json
python scripts/build_index.py     # build data/chunks.pkl

streamlit run app.py
```

## Known limits

- **6 of 25 sources are unreachable (SID/KIM PDFs).** The Large Cap, Multicap, ELSS, and Liquid SID PDFs and the Multicap/ELSS KIM PDFs (all under `assets-netstorage.growwmf.in`) return HTTP 404 even with a real browser User-Agent — they appear to have moved or been taken down, not merely blocked. The 4 scheme detail pages and the consolidated monthly factsheet (both confirmed live) independently cover the same six fact types, so nothing in `facts.json` is unsourced. See `data/fetch_log.json` for the full per-URL result.
- **Groww Multicap Fund's expense ratio is not published** on its official scheme page as of the fetch date. The app reports this honestly ("not published... as of [date]") rather than guessing or pulling a number from an unrelated fund.
- **The consolidated factsheet PDF has unreliable text extraction.** `pypdf` pulls readable-looking text out of it, but exact string matching against it fails in places (likely a font/encoding quirk in the PDF), so it's kept in the retrieval corpus for general chunk matching but was *not* used as a source for hand-verified numbers in `facts.json`.
- **The capital-gains-statement / CAS pages are instructional only.** CAMS/KFintech's actual statement delivery is behind a PAN + password + CAPTCHA mailback flow, so the app can only explain the *process*, not fetch an actual statement (which is correct — it shouldn't handle that kind of data anyway, see PII guardrail).
- **Retrieval is TF-IDF (lexical), not semantic embeddings.** Chosen over `sentence-transformers` after that pulled a broken torch/numpy combination in this environment; TF-IDF also installs far lighter for free-tier hosting and performs well here since the queries use precise domain terms that appear near-verbatim in the source pages. It will be weaker on paraphrased/synonym-heavy queries than a dense embedding model would be.
- **Extractive answers for open-ended queries (e.g. the statement-download question) can read slightly disjointed** — they're built from the 3 most query-relevant *sentences* in the best-matching chunk, not a fluent generative rewrite, since there's no live LLM call. Still factual and cited, just less smooth than natural prose.
- **`sebi.gov.in` failed to resolve via this environment's local DNS resolver** (works fine via public DNS) — `fetch_sources.py` pins its IP as a workaround. If deploying somewhere with normal DNS, this is unnecessary but harmless.

## Files

- `sources.md` — the 25-URL source list with category/scheme/format tags and fetch status
- `scripts/sources_data.py` — same source list, machine-readable (single source of truth for the fetch/build scripts)
- `scripts/fetch_sources.py`, `scripts/build_facts.py`, `scripts/build_index.py` — the ingestion pipeline
- `scripts/test_routing.py` — sanity test of the query router against the canonical question types + guardrails
- `data/` — generated: `raw/*.txt`, `facts.json`, `chunks.pkl`, `fetch_log.json`
- `app.py` — the Streamlit app
- `sample_qa.md` — 10 real Q&A pairs from the finished app
- `DISCLAIMER.md` — the exact UI disclaimer text
