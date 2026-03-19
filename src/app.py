"""Streamlit main entrypoint (Issue 1 skeleton)."""

import streamlit as st


def main() -> None:
    """Render a minimal app shell for progressive implementation."""
    st.set_page_config(page_title="Ethical Public Leads Scraper")
    st.title("Ethical Public Leads Scraper")
    st.caption("Issue 1 skeleton: structure only, logic will be added progressively.")

    st.info(
        "Ethical use only: scrape public sources, respect robots.txt and site terms, keep processing local."
    )
    st.write(
        "TODO(milestone-2-3-4): wire scraping (M2), enrichment/indexing (M3), and search/export UI (M4)."
    )


if __name__ == "__main__":
    main()
