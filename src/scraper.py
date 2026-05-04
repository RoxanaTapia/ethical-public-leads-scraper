"""Core scraping module: directory listing extraction with robots checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.utils import is_scraping_allowed, load_config, polite_delay

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "config.yaml"


def _strip_text(el: Any) -> str:
    if el is None:
        return ""
    return el.get_text(strip=True)


def _website_from_element(el: Any, page_url: str) -> str:
    if el is None:
        return ""
    if getattr(el, "name", None) == "a":
        href = el.get("href")
        if href:
            return urljoin(page_url, href.strip())
    nested = el.select_one("a[href]")
    if nested is not None:
        href = nested.get("href")
        if href:
            return urljoin(page_url, href.strip())
    return _strip_text(el)


def _email_from_element(el: Any) -> str:
    if el is None:
        return ""
    if getattr(el, "name", None) == "a":
        href = el.get("href") or ""
        if href.lower().startswith("mailto:"):
            return urlparse(href).path or href[7:].split("?")[0].strip()
    nested = el.select_one("a[href^='mailto:'], a[href^='MAILTO:']")
    if nested is not None:
        href = nested.get("href") or ""
        low = href.lower()
        if low.startswith("mailto:"):
            return urlparse(href).path or href[7:].split("?")[0].strip()
    return _strip_text(el)


def scrape_directory(url: str, config: dict | None = None) -> list[dict]:
    """Fetch a directory page and extract one record per listing card.

    Uses ``target_selectors`` from config (listing + field selectors relative
    to each card). Respects robots.txt via :func:`is_scraping_allowed` and
    applies ``polite_delay`` before the HTTP GET.
    """
    if config is None:
        config = load_config(DEFAULT_CONFIG_PATH)

    polite_delay(config["delay_sec"])

    if not is_scraping_allowed(url, user_agent=config["user_agent"]):
        return []

    selectors = config["target_selectors"]

    try:
        resp = requests.get(
            url,
            timeout=config["timeout_sec"],
            headers={"User-Agent": config["user_agent"]},
        )
    except requests.RequestException:
        return []

    if resp.status_code >= 400:
        return []

    soup = BeautifulSoup(resp.content, "html.parser")
    cards = soup.select(selectors["listing"])

    out: list[dict] = []
    for card in cards:
        name_el = card.select_one(selectors["name"])
        website_el = card.select_one(selectors["website"])
        email_el = card.select_one(selectors["email"])
        phone_el = card.select_one(selectors["phone"])

        out.append(
            {
                "name": _strip_text(name_el),
                "website": _website_from_element(website_el, url),
                "email": _email_from_element(email_el),
                "phone": _strip_text(phone_el),
                "source_url": url,
            }
        )

    return out
