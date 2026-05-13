"""Tests for enrich_lead (no live LLM)."""

from __future__ import annotations

import os
from unittest.mock import patch

from src.extractor import enrich_lead


def test_enrich_lead_no_env_returns_same_dict() -> None:
    lead = {"name": "X", "website": "https://x.org"}
    with patch.dict(os.environ, {}, clear=True):
        out = enrich_lead(lead)
        assert out is lead


def test_enrich_lead_missing_keys_noop() -> None:
    lead = {"name": "Y"}
    env = {k: os.environ[k] for k in ("LLM_API_KEY", "LLM_MODEL") if k in os.environ}
    try:
        for k in ("LLM_API_KEY", "LLM_MODEL"):
            os.environ.pop(k, None)
        assert enrich_lead(lead) is lead
    finally:
        os.environ.update(env)
