from __future__ import annotations

from typing import Any, Dict


def build_shadow_authority_ledger(sender_id: str, inbound_text: str) -> Dict[str, Any]:
    ledger: Dict[str, Any] = {
        "mission": "P4.95H2",
        "mode": "SHADOW_ONLY",
        "sender_id": str(sender_id or "")[:120],
        "inbound_preview": str(inbound_text or "")[:300],
        "ok": False,
        "candidates": [],
        "selection": None,
        "error": None,
    }

    try:
        from app.runtime.assisted_bypass_runtime import build_universal_assisted_context
        from app.runtime.final_authority_selector import select_final_authority_candidate

        ctx = build_universal_assisted_context(inbound_text)
        render = ctx.get("authority_render") if isinstance(ctx, dict) else None

        if isinstance(render, dict):
            ledger["candidates"].append({
                "source": "universal_authority_renderer",
                "text": str(render.get("text", "")),
                "safe": render.get("quality", {}).get("safe") is True,
                "send_to_user": render.get("send_to_user") is True,
            })

        ledger["candidates"].append({
            "source": "legacy_runtime_observation",
            "text": "legacy runtime still owns final reply",
            "safe": True,
            "send_to_user": False,
        })

        ledger["selection"] = select_final_authority_candidate(ledger["candidates"])
        ledger["ok"] = True
        return ledger

    except Exception as exc:
        ledger["error"] = f"{type(exc).__name__}: {exc}"
        return ledger
