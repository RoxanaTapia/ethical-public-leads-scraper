"""AI enrichment and RAG-like querying module (Issue 1 skeleton)."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _lead_text_block(lead: dict[str, Any]) -> str:
    lines: list[str] = []
    for key in ("name", "website", "email", "phone", "source_url"):
        if key not in lead:
            continue
        val = lead[key]
        if val is None:
            continue
        if isinstance(val, str) and not val.strip():
            continue
        lines.append(f"{key}: {val}")
    if lines:
        return "\n".join(lines)
    for k, v in lead.items():
        if isinstance(v, str) and v.strip():
            lines.append(f"{k}: {v}")
    return "\n".join(lines)


def enrich_lead(lead: dict) -> dict:
    """Optionally add a ``summary`` field using LangChain when LLM env vars are set.

    Requires ``LLM_API_KEY`` and ``LLM_MODEL``. If either is missing, or the
    model/provider cannot be loaded or invoked, returns ``lead`` unchanged.
    Original keys are never removed; on success a ``summary`` key is added or updated.
    """
    api_key = (os.getenv("LLM_API_KEY") or "").strip()
    model_name = (os.getenv("LLM_MODEL") or "").strip()
    if not api_key or not model_name:
        return lead

    text_in = _lead_text_block(lead)
    if not text_in.strip():
        return lead

    provider = (os.getenv("LLM_PROVIDER") or "openai").strip().lower() or "openai"

    try:
        from langchain.chat_models import init_chat_model
        from langchain_core.messages import HumanMessage

        llm = init_chat_model(
            model_name,
            model_provider=provider,
            api_key=api_key,
        )
        prompt = (
            "In one concise sentence, summarize this directory lead for a CRM. "
            "Use only the facts given; do not invent details.\n\n"
            f"{text_in}"
        )
        msg = llm.invoke([HumanMessage(content=prompt)])
        raw = getattr(msg, "content", None)
        summary = (raw if isinstance(raw, str) else str(msg)).strip()
        if not summary:
            return lead
        out = dict(lead)
        out["summary"] = summary
        return out
    except Exception:
        return lead


def query_leads(query: str, leads: list[dict]) -> list[dict]:
    """
    Placeholder for retrieval/query over enriched leads.

    TODO(milestone-4-full-pipeline-search-export): Add query/retrieval logic for search + export flow.
    """
    _ = query
    return leads
