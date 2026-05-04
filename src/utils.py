"""Helper utilities module (Issue 1 skeleton)."""

from __future__ import annotations

import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import pandas as pd
import yaml

# Used when fetching robots.txt and for can_fetch when caller omits user_agent.
_DEFAULT_ROBOTS_UA = "EthicalPublicLeadsBot/1.0"
# Network timeout for robots.txt fetch (seconds); fail-closed on timeout.
_ROBOTS_FETCH_TIMEOUT_SEC = 10.0

_REQUIRED_TOP_KEYS = (
    "delay_sec",
    "chunk_size",
    "timeout_sec",
    "user_agent",
    "target_selectors",
)
_REQUIRED_SELECTOR_KEYS = ("listing", "name", "website", "email", "phone")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load YAML config from ``path`` and validate structure and selector strings.

    Raises:
        ValueError: missing keys, wrong types, or any required selector empty
            after strip.
    """
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"Config file does not exist or is not a file: {p}")

    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as e:
        raise ValueError(f"Cannot read config file {p}: {e}") from e

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config {p}: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping, got {type(data).__name__}")

    missing = [k for k in _REQUIRED_TOP_KEYS if k not in data]
    if missing:
        raise ValueError(
            "Config missing required top-level key(s): "
            + ", ".join(repr(k) for k in missing)
        )

    ts = data["target_selectors"]
    if not isinstance(ts, dict):
        raise ValueError(
            "target_selectors must be a mapping, "
            f"got {type(ts).__name__}"
        )

    missing_sel = [k for k in _REQUIRED_SELECTOR_KEYS if k not in ts]
    if missing_sel:
        raise ValueError(
            "target_selectors missing required key(s): "
            + ", ".join(repr(k) for k in missing_sel)
        )

    for key in _REQUIRED_SELECTOR_KEYS:
        val = ts[key]
        if not isinstance(val, str):
            raise ValueError(
                f"target_selectors[{key!r}] must be a non-empty string, "
                f"got {type(val).__name__}"
            )
        if not val.strip():
            raise ValueError(
                f"target_selectors[{key!r}] must be a non-empty string "
                "(after strip)"
            )

    return data


def polite_delay(delay_sec: float) -> None:
    """Sleep for ``delay_sec`` seconds between requests; no-op if delay is zero or negative."""
    if delay_sec <= 0:
        return
    time.sleep(delay_sec)


def is_scraping_allowed(url: str, user_agent: str | None = None) -> bool:
    """Return whether ``url`` may be fetched per robots.txt for that origin.

    Uses :class:`urllib.robotparser.RobotFileParser`. If robots.txt cannot be
    fetched, times out, or cannot be applied safely, returns ``False`` (fail-closed).
    """
    ua = (user_agent or _DEFAULT_ROBOTS_UA).strip() or _DEFAULT_ROBOTS_UA

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False

    origin = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = urljoin(origin + "/", "/robots.txt")

    try:
        req = urllib.request.Request(robots_url, headers={"User-Agent": ua})
        with urllib.request.urlopen(
            req, timeout=_ROBOTS_FETCH_TIMEOUT_SEC
        ) as resp:
            raw = resp.read()
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
        ValueError,
    ):
        return False

    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        return False

    lines = text.splitlines()
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.parse(lines)
    except Exception:
        return False

    try:
        return rp.can_fetch(ua, url)
    except Exception:
        return False


_STANDARD_STRING_KEYS = ("name", "website", "email", "phone", "source_url")
_WS_RE = re.compile(r"\s+")


def _strip_cell(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _normalize_phone(value: Any) -> str:
    s = _strip_cell(value)
    if not s:
        return ""
    return _WS_RE.sub(" ", s)


def _dedupe_key_row(row: pd.Series) -> str:
    w = row["website"] if "website" in row.index else None
    if isinstance(w, str) and w.strip():
        return f"website:{w.strip()}"
    name = row["name"] if "name" in row.index else ""
    email = row["email"] if "email" in row.index else ""
    n = name.strip() if isinstance(name, str) else ""
    e = email.strip().lower() if isinstance(email, str) else ""
    return f"name_email:{n}|{e}"


def clean_dataframe(records: list[dict]) -> list[dict]:
    """Normalize tabular lead records: strip text, normalize email/phone, dedupe.

    Deduplication uses ``website`` when it is non-empty; otherwise ``name`` + ``email``.
    Column keys from the input are preserved; new columns are not added.
    """
    if not records:
        return []

    df = pd.DataFrame(records)

    for key in _STANDARD_STRING_KEYS:
        if key in df.columns:
            df[key] = df[key].map(_strip_cell)

    if "email" in df.columns:
        df["email"] = df["email"].map(
            lambda x: x.lower() if isinstance(x, str) else x
        )

    if "phone" in df.columns:
        df["phone"] = df["phone"].map(_normalize_phone)

    df = df.copy()
    df["_dedupe_key"] = df.apply(_dedupe_key_row, axis=1)
    df = df.drop_duplicates(subset=["_dedupe_key"], keep="first")
    df = df.drop(columns=["_dedupe_key"])

    out: list[dict] = df.to_dict(orient="records")
    for row in out:
        for k, v in list(row.items()):
            if v is None or (isinstance(v, float) and pd.isna(v)):
                row[k] = None
    return out
