from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .config import BrainSettings


def _stable_id(decision: dict[str, Any]) -> str:
    raw = json.dumps(decision, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12].upper()


def normalize_plan(payload: dict[str, Any], settings: BrainSettings) -> dict[str, Any]:
    normalized = deepcopy(payload)
    evidence_urls = {
        str(item.get("source_url", "")).strip()
        for item in normalized.get("evidence", [])
        if str(item.get("source_url", "")).strip()
    }

    accepted = []
    rejected_internal = []

    for raw in normalized.get("decisions", []):
        decision = dict(raw)
        confidence = float(decision.get("confidence", 0.0))
        refs = [str(url).strip() for url in decision.get("evidence_refs", []) if str(url).strip()]
        valid_refs = [url for url in refs if url in evidence_urls]

        if confidence < settings.minimum_confidence:
            rejected_internal.append({
                "trend": decision.get("content_id", "unknown"),
                "reason": f"confidence {confidence} abaixo de {settings.minimum_confidence}",
            })
            continue

        if not valid_refs:
            rejected_internal.append({
                "trend": decision.get("content_id", "unknown"),
                "reason": "decisão sem fonte válida vinculada",
            })
            continue

        decision["evidence_refs"] = valid_refs
        decision["content_id"] = decision.get("content_id") or f"ELDORA_{_stable_id(decision)}"
        decision["status"] = "PLANNED"
        accepted.append(decision)

    normalized["decisions"] = accepted[: settings.max_decisions]
    normalized["rejected_trends"] = list(normalized.get("rejected_trends", [])) + rejected_internal
    normalized["guardrails"] = settings.guardrails
    normalized["schema"] = "eldora.content.brain.plan.v1"
    return normalized