"""Tests for scrape_directory (no live HTTP; HTML from fixtures/mocks)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from src.scraper import BUNDLED_DEMO_URL, scrape_directory

_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "sample_directory.html"
_SAMPLE_HTML = _FIXTURE_PATH.read_text(encoding="utf-8")

_MINIMAL_CONFIG = {
    "delay_sec": 0,
    "chunk_size": 500,
    "timeout_sec": 30,
    "user_agent": "TestBot/1.0",
    "target_selectors": {
        "listing": ".listing",
        "name": ".name",
        "website": ".website",
        "email": ".email",
        "phone": ".phone",
    },
}


def _mock_response(html: str, status_code: int = 200) -> Mock:
    r = Mock()
    r.status_code = status_code
    r.text = html
    r.content = html.encode("utf-8")
    return r


@patch("src.scraper.requests.get")
@patch("src.scraper.is_scraping_allowed", return_value=True)
@patch("src.scraper.polite_delay")
def test_scrape_directory_extracts_listings(
    _mock_delay: Mock,
    _mock_allowed: Mock,
    mock_get: Mock,
) -> None:
    mock_get.return_value = _mock_response(_SAMPLE_HTML)

    results = scrape_directory("https://example.com/directory", config=_MINIMAL_CONFIG)

    assert len(results) == 2
    required = {"name", "website", "email", "phone", "source_url"}
    for row in results:
        assert required <= row.keys()

    assert results[0]["name"] == "Acme Public Benefit Corp"
    assert results[0]["website"] == "https://example.com/orgs/acme"
    assert results[0]["email"] == "hello@acme.example.org"
    assert results[0]["phone"] == "+1 (555) 010-2030"
    assert results[0]["source_url"] == "https://example.com/directory"

    assert results[1]["name"] == "Beta Cooperative"
    assert results[1]["website"] == "https://beta.example.net/"
    assert results[1]["email"] == "contact@beta.example.net"
    assert results[1]["phone"] == "555-0101"


@patch("src.scraper.requests.get")
@patch("src.scraper.is_scraping_allowed", return_value=False)
@patch("src.scraper.polite_delay")
def test_scrape_directory_blocked_by_robots(
    _mock_delay: Mock,
    _mock_allowed: Mock,
    mock_get: Mock,
) -> None:
    results = scrape_directory("https://example.com/directory", config=_MINIMAL_CONFIG)
    assert results == []
    mock_get.assert_not_called()


@patch("src.scraper.requests.get")
@patch("src.scraper.is_scraping_allowed", return_value=True)
@patch("src.scraper.polite_delay")
def test_scrape_directory_http_error_returns_empty(
    _mock_delay: Mock,
    _mock_allowed: Mock,
    mock_get: Mock,
) -> None:
    mock_get.return_value = _mock_response("<html></html>", status_code=404)
    results = scrape_directory("https://example.com/missing", config=_MINIMAL_CONFIG)
    assert results == []


@patch("src.scraper.requests.get")
@patch("src.scraper.is_scraping_allowed", return_value=True)
@patch("src.scraper.polite_delay")
def test_scrape_directory_request_exception_returns_empty(
    _mock_delay: Mock,
    _mock_allowed: Mock,
    mock_get: Mock,
) -> None:
    import requests as req_lib

    mock_get.side_effect = req_lib.Timeout("timed out")
    results = scrape_directory("https://example.com/slow", config=_MINIMAL_CONFIG)
    assert results == []


def test_scrape_directory_bundled_demo_extracts_three_rows() -> None:
    """Bundled demo HTML ships in demo/index.html (no HTTP)."""
    results = scrape_directory(BUNDLED_DEMO_URL, config=_MINIMAL_CONFIG)
    assert len(results) == 3
    assert all(row["source_url"] == BUNDLED_DEMO_URL for row in results)
    assert "Riverbend" in results[0]["name"]
