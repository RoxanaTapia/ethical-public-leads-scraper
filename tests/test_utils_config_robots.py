"""Tests for load_config and is_scraping_allowed (mocked network)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.utils import is_scraping_allowed, load_config

_VALID_YAML = """\
delay_sec: 1
chunk_size: 500
timeout_sec: 30
user_agent: "TestBot/1.0"
target_selectors:
  listing: ".listing"
  name: ".name"
  website: ".website"
  email: ".email"
  phone: ".phone"
"""


def _mock_urlopen_response(body: bytes) -> MagicMock:
    inner = MagicMock()
    inner.read.return_value = body
    cm = MagicMock()
    cm.__enter__.return_value = inner
    cm.__exit__.return_value = False
    return cm


def test_load_config_ok(tmp_path: Path) -> None:
    p = tmp_path / "cfg.yaml"
    p.write_text(_VALID_YAML, encoding="utf-8")
    cfg = load_config(p)
    assert cfg["delay_sec"] == 1
    assert cfg["target_selectors"]["listing"] == ".listing"


def test_load_config_missing_key_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text(
        "delay_sec: 1\nchunk_size: 500\ntimeout_sec: 30\nuser_agent: x\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required top-level"):
        load_config(p)


def test_load_config_empty_selector_raises(tmp_path: Path) -> None:
    p = tmp_path / "empty_sel.yaml"
    p.write_text(
        _VALID_YAML.replace('listing: ".listing"', 'listing: ""'),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="listing"):
        load_config(p)


def test_load_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        load_config(tmp_path / "nope.yaml")


@patch("urllib.request.urlopen")
def test_is_scraping_allowed_true_when_robots_allows(mock_urlopen: MagicMock) -> None:
    mock_urlopen.return_value = _mock_urlopen_response(
        b"User-agent: *\nAllow: /\n"
    )
    assert is_scraping_allowed("https://example.com/dir", user_agent="TestBot/1.0") is True


@patch("urllib.request.urlopen")
def test_is_scraping_allowed_false_when_fetch_fails(mock_urlopen: MagicMock) -> None:
    import urllib.error

    mock_urlopen.side_effect = urllib.error.URLError("network down")
    assert is_scraping_allowed("https://example.com/page", user_agent="Bot/1") is False


def test_is_scraping_allowed_false_for_non_http_url() -> None:
    assert is_scraping_allowed("ftp://example.com/x", user_agent="Bot/1") is False


@patch("urllib.request.urlopen")
def test_is_scraping_allowed_false_when_disallow_all(mock_urlopen: MagicMock) -> None:
    mock_urlopen.return_value = _mock_urlopen_response(
        b"User-agent: *\nDisallow: /\n"
    )
    assert (
        is_scraping_allowed("https://example.org/public", user_agent="TestBot/1.0")
        is False
    )
