"""Write the structured per-scheme facts table (data/facts.json).

Values below were hand-verified directly against the freshly fetched text in
data/raw/scheme-*.txt (see fetch_sources.py) on the date noted in FETCHED_ON.
This is NOT a generic auto-extractor: with only 4 schemes x 6 fact types, hand
verification against the live page text is safer than regex extraction, which
risks silently pulling the wrong number from a template-driven page.

Each fact carries its own source URL so the app can cite it directly.
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent

FETCHED_ON = "2026-08-27"

SCHEME_URLS = {
    "Large Cap": "https://www.growwmf.in/mutual-funds/groww-large-cap-fund-direct-growth",
    "Multicap": "https://www.growwmf.in/mutual-funds/groww-multicap-fund-direct-growth",
    "ELSS Tax Saver": "https://www.growwmf.in/mutual-funds/groww-elss-tax-saver-fund-direct-growth",
    "Liquid": "https://www.growwmf.in/mutual-funds/groww-liquid-fund-direct-growth",
}

FACTS = {
    "Large Cap": {
        "category": "Large Cap Equity",
        "expense_ratio": "1.27% (inclusive of GST)",
        "exit_load": "1% if redeemed or switched out within 7 days from the date of allotment; Nil after 7 days",
        "min_sip": "₹500",
        "min_lumpsum": "₹500",
        "lock_in": None,
        "riskometer": "Very High",
        "benchmark": "Nifty 100 TRI (additional benchmark: BSE Sensex TRI)",
    },
    "Multicap": {
        "category": "Multi Cap Equity",
        "expense_ratio": None,  # not published on the official scheme page as of FETCHED_ON
        "exit_load": "1% if redeemed or switched out within 1 year from the date of allotment; Nil after 1 year",
        "min_sip": "₹500",
        "min_lumpsum": "₹500",
        "lock_in": None,
        "riskometer": "Very High",
        "benchmark": "Nifty 50 TRI (additional benchmark: NIFTY 500 Multicap 50:25:25 TRI)",
    },
    "ELSS Tax Saver": {
        "category": "ELSS (Tax Saver)",
        "expense_ratio": "0.50% (inclusive of GST)",
        "exit_load": "Nil",
        "min_sip": "₹500",
        "min_lumpsum": "₹500",
        "lock_in": "3 years",
        "riskometer": "Very High",
        "benchmark": "Nifty 50 TRI (additional benchmark: Nifty 500 TRI)",
    },
    "Liquid": {
        "category": "Liquid / Debt",
        "expense_ratio": "0.22% (inclusive of GST)",
        "exit_load": "Tiered: 0.007% if exited within 1 day of purchase, decreasing daily, to Nil after 7 days",
        "min_sip": "₹500",
        "min_lumpsum": "₹500",
        "lock_in": None,
        "riskometer": "Moderate",
        "benchmark": "CRISIL Liquid Debt A-I Index (additional benchmark: Crisil 1 Yr T-Bill Index)",
    },
}


def main():
    out = {}
    for scheme, facts in FACTS.items():
        out[scheme] = {
            **facts,
            "source_url": SCHEME_URLS[scheme],
            "fetched_on": FETCHED_ON,
        }
    (ROOT / "data" / "facts.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote data/facts.json for {len(out)} schemes.")
    missing = [s for s, f in FACTS.items() if any(v is None for k, v in f.items() if k not in ("lock_in",))]
    if missing:
        print(f"Note: schemes with a genuinely missing (not fabricated) fact: {missing}")


if __name__ == "__main__":
    main()
