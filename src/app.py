"""Streamlit main entrypoint: URL → scrape → clean → enrich → export."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Streamlit executes this file with ``src/`` on sys.path, not the repo root, so
# ``from src.…`` only works once the parent directory is importable.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from src.extractor import enrich_lead
from src.scraper import BUNDLED_DEMO_URL, DEFAULT_CONFIG_PATH, scrape_directory
from src.utils import clean_dataframe, load_config


def main() -> None:
    st.set_page_config(
        page_title="Ethical Public Leads Scraper",
        initial_sidebar_state="expanded",
    )
    st.title("Ethical Public Leads Scraper")
    st.caption(
        "Public directories only — respect robots.txt, terms of use, and rate limits."
    )

    st.info(
        "Ethical use only: scrape public sources, respect robots.txt and site terms, "
        "keep processing local."
    )

    default_config_str = str(DEFAULT_CONFIG_PATH)
    default_demo_url = BUNDLED_DEMO_URL
    st.caption(
        "Default URL reads the bundled synthetic **demo/** page from the repo (works on "
        "Streamlit Cloud). To exercise **HTTP + robots.txt**, run "
        "`python -m http.server 8765` from the `demo/` folder and use "
        "`http://127.0.0.1:8765/index.html` instead."
    )

    st.subheader("Run")
    with st.form("pipeline"):
        config_path = st.text_input(
            "Config path",
            value=default_config_str,
            help="YAML file with delay_sec, timeout_sec, user_agent, and target_selectors.",
        )
        url = st.text_input(
            "Directory page URL",
            value=default_demo_url,
            help="Use `builtin:demo` for the shipped synthetic HTML (no local server). "
            "Use a public https:// URL for a hosted directory page.",
        )
        run = st.form_submit_button("Run pipeline", type="primary")

    if run:
        if not url or not url.strip():
            st.warning("Enter a URL.")
            return
        p = Path(config_path.strip()).expanduser()
        try:
            cfg = load_config(p)
        except ValueError as e:
            st.error(str(e))
            return

        spinner_msg = (
            "Loading bundled demo…"
            if url.strip().lower() == BUNDLED_DEMO_URL.lower()
            else "Scraping (robots + polite delay)…"
        )
        with st.spinner(spinner_msg):
            try:
                raw = scrape_directory(url.strip(), config=cfg)
            except Exception as e:
                st.error(f"Scrape failed: {e}")
                return

        if not raw:
            st.warning(
                "No rows extracted. Check selectors in config, robots.txt, or the URL."
            )

        cleaned = clean_dataframe(raw)
        enriched = [enrich_lead(dict(row)) for row in cleaned]

        st.session_state["leads"] = enriched
        st.session_state["last_url"] = url.strip()

    leads: list[dict] | None = st.session_state.get("leads")

    if leads:
        st.subheader("Preview")
        st.write(f"Rows: **{len(leads)}**")
        if st.session_state.get("last_url"):
            st.caption(f"Source: `{st.session_state['last_url']}`")

        df = pd.DataFrame(leads)
        st.dataframe(df, use_container_width=True)

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        json_bytes = json.dumps(leads, indent=2, ensure_ascii=False).encode("utf-8")

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name="leads.csv",
                mime="text/csv",
            )
        with c2:
            st.download_button(
                label="Download JSON",
                data=json_bytes,
                file_name="leads.json",
                mime="application/json",
            )
    else:
        st.write(
            "Submit **Run pipeline** above to scrape, clean, optionally enrich "
            "(when LLM env vars are set), and export."
        )


if __name__ == "__main__":
    main()
