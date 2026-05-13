# Ethical Public Leads Scraper

**Turn public directory pages into structured lead data**—with guardrails, optional AI summaries, and exports you can hand to a CRM or spreadsheet.

This repository is a **Phase 1 work-in-progress (WIP) portfolio build**: a small, transparent pipeline you can run locally to demonstrate responsible web data collection and practical Python engineering (Streamlit UI, config-driven scraping, tests).

---

## At a glance

| | |
|--|--|
| **What it does** | Reads a public listing URL, extracts name / website / email / phone per card, deduplicates, optionally adds a one-line LLM summary, then exports **CSV** or **JSON**. |
| **Who it is for** | Teams or individuals who need **ethical, explainable** extraction from **public** directories—not logged-in portals or bulk evasion of site policy. |
| **How you run it** | Local **Streamlit** app + YAML config; **Python 3.12+** recommended (see `requirements.txt`). |
| **License** | MIT — see [LICENSE](LICENSE). |

---

## Why this exists (outcomes)

- **Trust:** Respects `robots.txt`, uses configurable delays and a clear User-Agent, and keeps processing **on your machine**.
- **Clarity:** Selectors and timing live in one YAML file—easy to review with a client or teammate.
- **Delivery:** Preview in the browser, then download the same dataset as CSV or JSON for the next step in your workflow.

---

## What you get in the app

When you run Streamlit, you typically see:

1. **Sidebar** — Target URL, path to the YAML config, and a **Run pipeline** action.  
2. **Main area** — Row count, a **table preview** of extracted (and cleaned) leads.  
3. **Exports** — **Download CSV** and **Download JSON** for the current result set.

*(Optional: add a product screenshot to `docs/app-preview.png` and link it here for proposals—`![Preview](docs/app-preview.png)`.)*

---

## Pipeline

```text
Public URL → robots.txt check → polite delay → fetch page → parse listings (CSS)
           → clean & dedupe → optional LLM summary per row → preview & export
```

- **Configuration:** [configs/config.yaml](configs/config.yaml) — `target_selectors` must match the HTML of your target page (`listing` plus `name`, `website`, `email`, `phone`). The repo ships **non-empty placeholder** selectors so validation passes; **replace them** before expecting real extractions on a live site.  
- **Application:** [src/app.py](src/app.py) — Wires loading config, scraping, cleaning, optional enrichment, and downloads.

---

## Scope and limitations (read before a client demo)

Be explicit about what this MVP **does not** try to solve:

- **Single page** — No built-in pagination across many result pages yet.  
- **Public content only** — No authentication flows, CAPTCHA bypass, or advice that would violate a site’s terms.  
- **Selector-dependent** — Quality depends on accurate CSS selectors for each target layout.  
- **Enrichment cost** — With LLM keys set, enrichment is **one model call per row**; large lists are better handled in a later batching milestone.  
- **Search in-app** — `query_leads` in [src/extractor.py](src/extractor.py) is still a stub; filtering happens outside the app or in a future release.

---

## Tech stack

**Language:** Python 3.12+ (recommended)

| Area | Libraries / tools |
|------|-------------------|
| UI | [Streamlit](https://streamlit.io/) |
| HTTP & HTML | `requests`, `beautifulsoup4` |
| Data | `pandas` |
| Config | `pyyaml` |
| Optional AI | `langchain`, `langchain-openai`, `python-dotenv` |
| Tests | `pytest` |

---

## Project structure

```text
.
├── src/
│   ├── app.py          # Streamlit UI and export
│   ├── scraper.py      # HTTP + BeautifulSoup extraction
│   ├── extractor.py    # Optional LLM enrichment
│   └── utils.py        # Config load, robots, delay, cleaning
├── configs/
│   └── config.yaml
├── tests/
├── .env.example
├── requirements.txt
├── pytest.ini
├── README.md
└── data/
```

---

## Ethics statement

Use this tool only for **publicly accessible** sources, respecting `robots.txt` and each site’s terms of use. Prefer **local** processing and transparent configuration when showing work to clients or employers.

---

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run src/app.py
```

### Optional LLM enrichment

Copy `.env.example` to `.env` and set at least **`LLM_API_KEY`** and **`LLM_MODEL`** to add a short `summary` field per lead. Leave them empty to skip API calls entirely.

### Run tests

```bash
pytest tests/ -v
```

Use the same virtual environment as above (`requirements.txt` includes `pytest`).

---

## Author & license

Copyright (c) 2026 Roxana Tapia. Released under the [MIT License](LICENSE).
