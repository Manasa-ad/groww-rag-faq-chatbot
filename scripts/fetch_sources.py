"""Fetch every URL in sources_data.SOURCES, extract plain text, save to data/raw/<id>.txt.
Logs per-URL success/failure to data/fetch_log.json.
"""
import json
import sys
import time
from pathlib import Path

import socket

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent))
from sources_data import SOURCES

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Some sandboxes can't resolve sebi.gov.in via the local resolver even though the
# site is up (confirmed reachable via public DNS / direct IP). Pin it here so the
# fetch doesn't spuriously fail on a network quirk unrelated to the source itself.
DNS_OVERRIDES = {
    "www.sebi.gov.in": "202.191.181.30",
}

_orig_getaddrinfo = socket.getaddrinfo


def _patched_getaddrinfo(host, *args, **kwargs):
    if host in DNS_OVERRIDES:
        host = DNS_OVERRIDES[host]
    return _orig_getaddrinfo(host, *args, **kwargs)


socket.getaddrinfo = _patched_getaddrinfo

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}


def extract_html_text(content: bytes) -> str:
    soup = BeautifulSoup(content, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def fetch_one(src: dict, retries: int = 2, timeout: int = 20) -> dict:
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(src["url"], headers=HEADERS, timeout=timeout)
            if resp.status_code != 200:
                last_err = f"HTTP {resp.status_code}"
                time.sleep(1)
                continue
            if src["format"] == "pdf":
                text = extract_pdf_text(resp.content)
            else:
                text = extract_html_text(resp.content)
            if len(text.strip()) < 50:
                last_err = "extracted text too short (likely JS-rendered or blocked)"
                time.sleep(1)
                continue
            out_path = RAW_DIR / f"{src['id']}.txt"
            out_path.write_text(text, encoding="utf-8")
            return {"id": src["id"], "url": src["url"], "status": "ok", "chars": len(text), "error": None}
        except Exception as e:
            last_err = str(e)
            time.sleep(1)
    return {"id": src["id"], "url": src["url"], "status": "failed", "chars": 0, "error": last_err}


def main():
    log = []
    for src in SOURCES:
        result = fetch_one(src)
        status_word = "OK" if result["status"] == "ok" else "FAIL"
        print(f"[{status_word}] {src['id']:<28} {result.get('chars', 0):>7} chars  {src['url']}")
        if result["status"] == "failed":
            print(f"         -> {result['error']}")
        log.append(result)

    (ROOT / "data" / "fetch_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")

    ok = sum(1 for r in log if r["status"] == "ok")
    print(f"\n{ok}/{len(log)} sources fetched successfully. Log written to data/fetch_log.json")


if __name__ == "__main__":
    main()
