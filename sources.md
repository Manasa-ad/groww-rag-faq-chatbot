# Source Corpus

**Fetch status:** 19/25 sources fetched successfully (verified via `scripts/fetch_sources.py`, log in `data/fetch_log.json`). The 6 SID/KIM PDFs (rows 6–11) returned HTTP 404 on direct fetch, even with a real browser User-Agent, confirming they're genuinely moved/removed, not blocked — the scheme detail pages and the consolidated factsheet (both confirmed live) cover the same facts (TER, exit load, min SIP, lock-in, riskometer, benchmark) so nothing in the facts table below is unsourced.

AMC: **Groww Mutual Fund** (growwmf.in, formerly Indiabulls Asset Management, SEBI RegID MF/068/11/03)
Schemes covered: Groww Large Cap Fund, Groww Multicap Fund, Groww ELSS Tax Saver Fund, Groww Liquid Fund

| # | URL | Category | Scheme | Format | Notes |
|---|-----|----------|--------|--------|-------|
| 1 | https://growwmf.in/about-us | amc-general | — | html | AMC identity/background |
| 2 | https://www.growwmf.in/mutual-funds/groww-large-cap-fund-direct-growth | amc-scheme | Large Cap | html | TER, exit load, min SIP, riskometer, benchmark |
| 3 | https://www.growwmf.in/mutual-funds/groww-multicap-fund-direct-growth | amc-scheme | Multicap | html | exit load, min SIP, riskometer, benchmark |
| 4 | https://www.growwmf.in/mutual-funds/groww-elss-tax-saver-fund-direct-growth | amc-scheme | ELSS Tax Saver | html | TER, exit load, min SIP, lock-in, riskometer, benchmark |
| 5 | https://www.growwmf.in/mutual-funds/groww-liquid-fund-direct-growth | amc-scheme | Liquid | html | TER, exit load, min SIP, riskometer, benchmark |
| 6 | https://assets-netstorage.growwmf.in/compliance_docs/Downloads/SID/SID_Groww%20Large%20Cap%20Fund%20.pdf | amc-scheme | Large Cap | pdf | SID — **confirmed unavailable (404) as of fetch date, see README known limits** |
| 7 | https://assets-netstorage.growwmf.in/compliance_docs/Downloads/SID/SID_Groww%20Multicap%20Fund.pdf | amc-scheme | Multicap | pdf | SID — **confirmed unavailable (404) as of fetch date, see README known limits** |
| 8 | https://assets-netstorage.growwmf.in/compliance_docs/Downloads/KIM/KIM_Groww%20Multicap%20Fund.pdf | amc-scheme | Multicap | pdf | KIM — **confirmed unavailable (404) as of fetch date, see README known limits** |
| 9 | https://assets-netstorage.growwmf.in/compliance_docs/Downloads/SID/SID_Groww%20ELSS%20Tax%20Saver%20Fund.pdf | amc-scheme | ELSS Tax Saver | pdf | SID — **confirmed unavailable (404) as of fetch date, see README known limits** |
| 10 | https://assets-netstorage.growwmf.in/compliance_docs/Downloads/KIM/KIM_Groww%20ELSS%20Tax%20Saver%20Fund.pdf | amc-scheme | ELSS Tax Saver | pdf | KIM — **confirmed unavailable (404) as of fetch date, see README known limits** |
| 11 | https://assets-netstorage.growwmf.in/compliance_docs/Downloads/SID/SID_Groww%20Liquid%20Fund.pdf | amc-scheme | Liquid | pdf | SID — **confirmed unavailable (404) as of fetch date, see README known limits** |
| 12 | https://assets-netstorage.growwmf.in/compliance_docs/Downloads/Fact%20Sheet/2025%20-%202026/Monthly%20Factsheet%20-%20Jan%2026.pdf | amc-general | all 4 | pdf | Confirmed live; consolidated factsheet, fallback source for TER/riskometer/benchmark |
| 13 | https://cms-resources.growwmf.in/uploads/FA_Qs_for_Investors_Valid_Handle_21419eab26.pdf | amc-general | — | pdf | Investor FAQs |
| 14 | https://growwmf.in/new-kyc-regulations | amc-general | — | html | KYC FAQs |
| 15 | https://groww.in/blog/how-to-get-capital-gains-statement-for-mutual-fund-investments | amc-general | — | html | How to download capital-gains statement (Groww platform) |
| 16 | https://www.mutualfundssahihai.com/en/what-riskometer-and-what-are-different-levels | amfi | — | html | What a riskometer is, risk levels |
| 17 | https://www.mutualfundssahihai.com/en/how-riskometer-scheme-derived | amfi | — | html | How a scheme's riskometer is derived |
| 18 | https://www.mutualfundssahihai.com/en/what-total-return-index-tri-mutual-fund | amfi | — | html | Why TRI is used for benchmarks |
| 19 | https://www.mutualfundssahihai.com/en/what-is-lock-in-period | amfi | — | html | ELSS lock-in explainer |
| 20 | https://www.mutualfundssahihai.com/en/what-are-expenses-incurred-mutual-fund-scheme | amfi | — | html | Expense ratio / TER explainer |
| 21 | https://www.mutualfundssahihai.com/en/what-are-loads | amfi | — | html | Exit load explainer |
| 22 | https://www.amfiindia.com/otherdata/listofbenchmarkindices | amfi | — | html | Official Tier-1 benchmark index list |
| 23 | https://www.sebi.gov.in/legal/circulars/oct-2020/circular-on-product-labeling-in-mutual-fund-schemes-risk-o-meter_47796.html | sebi | — | html | Riskometer product-labeling circular |
| 24 | https://www.sebi.gov.in/sebi_data/faqfiles/sep-2024/1727242783639.pdf | sebi | — | pdf | SEBI general mutual fund investor FAQs |
| 25 | https://mfs.kfintech.com/investor/General/CapitalGainsLossAccountStatement | amc-general | — | html | Groww MF's RTA (KFintech) capital-gains/account-statement page |
