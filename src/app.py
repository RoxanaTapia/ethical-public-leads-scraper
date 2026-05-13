"""Streamlit main entrypoint: URL → scrape → clean → enrich → export."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.extractor import enrich_lead
from src.scraper import DEFAULT_CONFIG_PATH, scrape_directory
from src.utils import clean_dataframe, load_config


def main() -> None:
    st.set_page_config(page_title="Ethical Public Leads Scraper")
    st.title("Ethical Public Leads Scraper")
    st.caption(
        "Public directories only — respect robots.txt, terms of use, and rate limits."
    )

    st.info(
        "Ethical use only: scrape public sources, respect robots.txt and site terms, "
        "keep processing local."
    )

    default_config_str = str(DEFAULT_CONFIG_PATH)
    config_path = st.sidebar.text_input(
        "Config path",
        value=default_config_str,
        help="YAML file with delay_sec, timeout_sec, user_agent, and target_selectors.",
    )
    url = st.sidebar.text_input(
        "Directory page URL",
        placeholder="https://example.org/public-directory",
    )

    run = st.sidebar.button("Run pipeline", type="primary")

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

        with st.spinner("Scraping (robots + polite delay)…"):
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
            "Enter a URL and config path, then **Run pipeline** to scrape, clean, "
            "optionally enrich (when LLM env vars are set), and export."
        )


if __name__ == "__main__":
    main()
