"""Tests for clean_dataframe."""

from __future__ import annotations

from src.utils import clean_dataframe


def test_clean_dataframe_empty() -> None:
    assert clean_dataframe([]) == []


def test_clean_dataframe_strips_and_dedupes_by_website() -> None:
    rows = [
        {
            "name": "  Acme  ",
            "website": "https://acme.org",
            "email": "HELLO@ACME.ORG",
            "phone": "555  123  4567",
            "source_url": "https://example.com/p1",
        },
        {
            "name": "Acme",
            "website": "https://acme.org",
            "email": "hello@acme.org",
            "phone": "555 123 4567",
            "source_url": "https://example.com/p1",
        },
    ]
    out = clean_dataframe(rows)
    assert len(out) == 1
    assert out[0]["name"] == "Acme"
    assert out[0]["email"] == "hello@acme.org"
    assert out[0]["phone"] == "555 123 4567"


def test_clean_dataframe_dedupes_by_name_email_when_no_website() -> None:
    rows = [
        {"name": "Beta", "website": "", "email": "b@b.org", "phone": "1"},
        {"name": "Beta", "website": "  ", "email": "B@B.ORG", "phone": "2"},
    ]
    out = clean_dataframe(rows)
    assert len(out) == 1
    assert out[0]["email"] == "b@b.org"
