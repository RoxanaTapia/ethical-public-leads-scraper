# Ethical Public Leads Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/RoxanaTapia/ethical-public-leads-scraper?sort=semver)](https://github.com/RoxanaTapia/ethical-public-leads-scraper/releases)

**Turn public directory pages into structured lead data**—with guardrails, optional AI summaries, and exports you can hand to a CRM or spreadsheet.

This repository is a **portfolio build** (MVP): a small, transparent pipeline you can run locally—or host on [Streamlit Community Cloud](#streamlit-community-cloud)—to demonstrate responsible web data collection and practical Python engineering (Streamlit UI, config-driven scraping, tests).

**On this page:** [At a glance](#at-a-glance) · [Pipeline](#pipeline) · [Quick start](#quick-start) · [Client demo walkthrough](#client-demo-walkthrough) · [Streamlit Community Cloud](#streamlit-community-cloud) · [Releases and branching](#releases-and-branching) · [Tests](#run-tests)

---

## At a glance

| | |
|--|--|
| **What it does** | Reads a public listing URL, extracts name / website / email / phone per card, deduplicates, optionally adds a one-line LLM summary, then exports **CSV** or **JSON**. |
| **Who it is for** | Teams or individuals who need **ethical, explainable** extraction from **public** directories—not logged-in portals or bulk evasion of site policy. |
| **How you run it** | Local **Streamlit** app + YAML config; **Python 3.12+** recommended (see `requirements.txt`). For a scripted stakeholder demo, use [Client demo walkthrough](#client-demo-walkthrough). |
| **Deploy** | [Streamlit Community Cloud](#streamlit-community-cloud) — use branch **`stable`**, main file **`src/app.py`**. Production-ish commits are tagged (see [Releases](https://github.com/RoxanaTapia/ethical-public-leads-scraper/releases)). |
| **License** | MIT — see [LICENSE](LICENSE). |

---

## Why this exists (outcomes)

- **Trust:** Respects `robots.txt`, uses configurable delays and a clear User-Agent, and keeps processing **on your machine**.
- **Clarity:** Selectors and timing live in one YAML file—easy to review with a client or teammate.
- **Delivery:** Preview in the browser, then download the same dataset as CSV or JSON for the next step in your workflow.

---

## What you get in the app

When you run Streamlit, you typically see:

1. **Run** (main page) — Target URL, path to the YAML config, and a **Run pipeline** button.  
2. **Main area** — Row count, a **table preview** of extracted (and cleaned) leads.  
3. **Exports** — **Download CSV** and **Download JSON** for the current result set.

*(Optional: add a product screenshot to `docs/app-preview.png` and link it here for proposals—`![Preview](docs/app-preview.png)`.)*

---

## Pipeline

```text
Public URL → robots.txt check → polite delay → fetch page → parse listings (CSS)
           → clean & dedupe → optional LLM summary per row → preview & export
```

- **Configuration:** [configs/config.yaml](configs/config.yaml) — `target_selectors` must match the HTML of your target page (`listing` plus `name`, `website`, `email`, `phone`). The bundled [`demo/`](demo/) page uses the same class names as the defaults so you can run a walkthrough **without** editing YAML; for other sites, update selectors to match their DOM.  
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
├── demo/
│   ├── index.html      # Synthetic directory markup (matches default selectors)
│   └── robots.txt      # Allow-all for local / static hosting demos
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

The next section is the **stakeholder-ready path** for showing a live extraction without touching a third-party website.

---

## Client demo walkthrough

Use this when you want a **repeatable, policy-safe** demo: the page is **synthetic** (fictitious organizations and example.com-style URLs), the markup matches the repo’s default selectors, and **`demo/robots.txt`** allows automated fetches on the same origin so the app’s `robots.txt` gate succeeds.

### What you are demonstrating

- **Transparency:** Configuration (`configs/config.yaml`) drives delays, User-Agent, and CSS selectors—easy to show on screen or in a slide deck.  
- **Guardrails:** The pipeline checks `robots.txt` before requesting the directory page and uses a polite delay between requests.  
- **Output:** After a successful run you get a **preview table**, plus **CSV** and **JSON** downloads you can hand to a client as “sample deliverable” artifacts.

### Before you start (two processes)

You need **two terminals** (or one terminal plus your IDE’s terminal): one serves the static demo HTML, the other runs Streamlit.

### Steps (about three minutes)

1. **Activate the same virtual environment** you created in [Quick start](#quick-start) and install dependencies if you have not already.  
2. **Serve the bundled demo site** from the `demo/` directory (port **8765** matches the app’s default URL):

   ```bash
   cd demo
   python -m http.server 8765
   ```

   Leave this process running. You can confirm it in a browser by opening `http://127.0.0.1:8765/index.html` and `http://127.0.0.1:8765/robots.txt`.

3. **Start the app** (from the **repository root**, not inside `demo/`):

   ```bash
   streamlit run src/app.py
   ```

4. In the **Run** form on the main page, keep the default **Config path** pointing at `configs/config.yaml` and the default **Directory page URL** (`http://127.0.0.1:8765/index.html`) unless you are using a hosted copy (see below). Submit **Run pipeline**.

5. **Walk through the result:** point out **three** extracted rows, the **source URL** caption, and the **Download CSV / JSON** buttons. If optional LLM keys are configured, mention the extra summary column as an add-on.

### Success checklist

| Check | What it means |
|------|----------------|
| Preview shows **3 rows** | Selectors and HTML line up; the demo server returned the page. |
| Fields look populated | Name, website, email, and phone were parsed from each `.listing` card. |
| Downloads work | The same data leaves the browser as portable files—typical handoff to analysis or a CRM import test. |

### If the preview is empty

- Confirm the **demo server** is still running and the URL opens in a browser.  
- Confirm you are using **`http://127.0.0.1:8765/index.html`** (or your deployed HTTPS equivalent) so **`/robots.txt`** on that **same host and port** is the file from `demo/robots.txt`. The scraper **does not** run when `robots.txt` is missing or unusable.  
- Wait for the configured **delay** in YAML before assuming a failure; the first request can take a few seconds.

### Hosted demo (remote clients)

To demo on a call without asking viewers to run a local server, deploy the **contents** of [`demo/`](demo/) to any static host so that **`index.html`** and **`robots.txt`** are both available from the **same site origin**. Use the public `https://…/index.html` URL in the **Directory page URL** field. The synthetic content stays clearly non-production and avoids scraping an unknown third party during a sales or interview conversation.

---

## Streamlit Community Cloud

Deploy from [share.streamlit.io](https://share.streamlit.io) using this repository.

| Setting | Value |
|--------|--------|
| **Repository** | `RoxanaTapia/ethical-public-leads-scraper` (public) |
| **Branch** | **`stable`** — tracks release-ready commits; day-to-day development stays on `main`. |
| **Main file** | **`src/app.py`** (Cloud runs from the repo root; paths in `st.image` / assets are relative to that root). |
| **Dependencies** | **`requirements.txt`** at the repository root |

**Secrets (optional LLM):** In the app **Settings → Secrets**, add the same variables you would put in `.env` (for example `LLM_API_KEY`, `LLM_MODEL`, and optionally `LLM_PROVIDER`). Never commit real keys to the repo.

**Bundled demo URL on Cloud:** The app defaults to `http://127.0.0.1:8765/index.html` for a **local** demo server. On Community Cloud, `127.0.0.1` is the **container**, not your laptop—so that default **will not** reach a server on your machine. For a hosted app, either paste a **public HTTPS** URL where you deployed [`demo/`](demo/) (with `robots.txt` on the same origin), or run the scraper against another allowed public directory whose selectors match your YAML.

---

## Releases and branching

| Branch | Role |
|--------|------|
| **`main`** | Integration branch; receives feature PRs. |
| **`stable`** | Release line for hosting (Streamlit Cloud, demos); updated when you cut a release. |

Version tags (for example **`v1.0.0`**) mark the same commits you trust for that release. **Release notes** live on [GitHub Releases](https://github.com/RoxanaTapia/ethical-public-leads-scraper/releases).

---

## Optional LLM enrichment

Copy `.env.example` to `.env` and set at least **`LLM_API_KEY`** and **`LLM_MODEL`** to add a short `summary` field per lead. Leave them empty to skip API calls entirely.

---

## Run tests

```bash
pytest tests/ -v
```

Use the same virtual environment as above (`requirements.txt` includes `pytest`).

---

## Author & license

Copyright (c) 2026 Roxana Tapia. Released under the [MIT License](LICENSE).
