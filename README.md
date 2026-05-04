# Ethical Public Leads Scraper

Phase 1 MVP: scrape a **public directory** URL with **CSS selectors** from config, **respect robots.txt**, **clean** and **dedupe** rows, optionally **enrich** each lead with an LLM when env vars are set, and **export** CSV/JSON from the Streamlit UI.

## Pipeline

```text
URL → robots.txt check → fetch page → parse listings → clean → enrich (optional) → preview / export
```

- **Config:** [`configs/config.yaml`](configs/config.yaml) — set `target_selectors` to match your target HTML (`listing` plus fields `name`, `website`, `email`, `phone`). Placeholders in the repo are non-empty strings required by validation; replace them before scraping a real site.
- **App:** [`src/app.py`](src/app.py) — sidebar URL + config path, run pipeline, download `leads.csv` / `leads.json`.

## Project Structure

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

## Ethics Statement

Use this tool only for publicly accessible sources, respecting robots.txt and each site's terms.
All processing should remain local-only.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run src/app.py
```

### Optional LLM enrichment

Copy `.env.example` to `.env` and set at least `LLM_API_KEY` and `LLM_MODEL` to add a short `summary` field per lead. Leave them empty to skip API calls entirely.

### Tests

```bash
pytest tests/ -v
```

Requires the same virtualenv and `pip install -r requirements.txt` (includes `pytest`).
