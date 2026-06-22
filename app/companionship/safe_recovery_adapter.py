from __future__ import annotations

import importlib
from typing import Any, Dict, List

# P19P36G_SAFE_RECOVERY_ADAPTER
# Shadow-only adapter: não altera resposta, não altera fluxo vivo.
# Apenas tenta recuperar sinais de módulos existentes com segurança.

RECOVERED_MODULES = [
    "app.runtime.followup_unified_resolver",
    "app.runtime.generic_topic_memory_engine",
    "app.runtime.memory_adapter",
    "app.runtime.memory_store",
    "app.vision.vision_memory_store",
]

def safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

def collect_recovered_context(sender: str, text: str, base_ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(base_ctx or {})
    try:
        ctx = collect_memory_shadow(sender, text, ctx)
    except Exception:
        pass
    try:
        ctx = attach_memory_fusion_shadow(sender, text, ctx)
    except Exception:
        pass
    recovered: List[Dict[str, Any]] = []

    for module_name in RECOVERED_MODULES:
        mod = safe_import(module_name)
        if not mod:
            continue

        payload = {"module": module_name, "signals": {}}

        for fn_name in ["get", "resolve", "recall", "load", "get_context", "get_memory", "get_profile"]:
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                try:
                    payload["signals"][fn_name] = str(fn(sender))[:500]
                except TypeError:
                    try:
                        payload["signals"][fn_name] = str(fn(sender, text))[:500]
                    except Exception:
                        pass
                except Exception:
                    pass

        if payload["signals"]:
            recovered.append(payload)

    ctx["recovered_shadow_context"] = recovered
    return ctx

def enrich_reply_shadow(sender: str, text: str, base_ctx: Dict[str, Any], reply: str) -> str:
    # Shadow mode: não modifica a resposta.
    return reply
# /P19P36G_SAFE_RECOVERY_ADAPTER


# P19P36H_SHADOW_TELEMETRY
import json
from pathlib import Path
from datetime import datetime, timezone

TELEMETRY = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")

def _safe_json_default(obj):
    try:
        return str(obj)
    except Exception:
        return "<unserializable>"

def record_shadow_telemetry(sender: str, text: str, ctx: dict, reply: str) -> None:
    try:
        TELEMETRY.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": sender or "unknown",
            "text": (text or "")[:300],
            "active_domain": (ctx or {}).get("active_domain"),
            "active_subject": (ctx or {}).get("active_subject"),
            "recovered_shadow_context_count": len((ctx or {}).get("recovered_shadow_context", [])),
            "recovered_shadow_context": (ctx or {}).get("recovered_shadow_context", []),
            "memory_shadow": (ctx or {}).get("p19p36k_memory_shadow", {}),
            "memory_fusion_shadow": (ctx or {}).get("p19p36l_memory_fusion_shadow", {}),
            "reply_preview": (reply or "")[:300],
        }
        with TELEMETRY.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, default=_safe_json_default) + "\n")
    except Exception:
        pass
# /P19P36H_SHADOW_TELEMETRY


# P19P36K_SAFE_MEMORY_ADAPTER_V2
def _p19p36k_normalize_memory_item(x):
    try:
        if isinstance(x, str):
            return x.strip()
        return str(x).strip()
    except Exception:
        return ""

def _p19p36k_get_memory_store():
    try:
        from app.runtime.memory_store import SimpleMemoryStore
        return SimpleMemoryStore()
    except Exception:
        return None

def remember_user_message(sender: str, text: str) -> bool:
    try:
        t = str(text or "").strip()
        if not t:
            return False
        store = _p19p36k_get_memory_store()
        if not store:
            return False
        store.save(sender or "unknown", t)
        return True
    except Exception:
        return False

def recall_user_history(sender: str, limit: int = 8):
    try:
        store = _p19p36k_get_memory_store()
        if not store:
            return []
        items = store.recall(sender or "unknown", int(limit))
        if not isinstance(items, list):
            return []
        clean = []
        for x in items:
            v = _p19p36k_normalize_memory_item(x)
            if v:
                clean.append(v)
        return clean[-int(limit):]
    except Exception:
        return []

def collect_memory_shadow(sender: str, text: str, base_ctx: dict | None = None) -> dict:
    ctx = dict(base_ctx or {})
    remembered = remember_user_message(sender, text)
    history = recall_user_history(sender, 8)

    ctx["p19p36k_memory_shadow"] = {
        "remembered": remembered,
        "history_count": len(history),
        "history": history,
    }
    return ctx
# /P19P36K_SAFE_MEMORY_ADAPTER_V2


# P19P36L_MEMORY_FUSION_SHADOW_SCORING
import re

_P19P36L_STOPWORDS = {
    "quero","como","para","com","sem","isso","esse","essa","qual","quais",
    "continue","prossiga","depois","então","entao","mais","sobre","fazer",
    "tenho","estou","você","voce","meu","minha","uma","um","por","que"
}

def _p19p36l_tokens(text: str):
    try:
        raw = re.findall(r"[a-zà-ÿ0-9]{3,}", str(text or "").lower())
        return [x for x in raw if x not in _P19P36L_STOPWORDS]
    except Exception:
        return []

def score_memory_relevance(text: str, history: list, active_subject: str = "", active_domain: str = "") -> dict:
    try:
        query_tokens = set(_p19p36l_tokens(" ".join([text or "", active_subject or "", active_domain or ""])))
        hits = []
        scored_items = []

        for item in history or []:
            item_text = str(item or "")
            item_tokens = set(_p19p36l_tokens(item_text))
            overlap = sorted(query_tokens.intersection(item_tokens))
            if overlap:
                hits.extend(overlap)
                scored_items.append({
                    "text": item_text[:240],
                    "overlap": overlap,
                    "score": min(1.0, len(overlap) / max(1, len(query_tokens)))
                })

        unique_hits = sorted(set(hits))
        base_score = min(1.0, len(unique_hits) / max(1, len(query_tokens)))

        # reforços por domínio
        domain_bonus = 0.0
        joined = " ".join([str(x).lower() for x in history or []])
        if active_domain and active_domain.lower() in joined:
            domain_bonus += 0.12
        if active_subject:
            subj_tokens = set(_p19p36l_tokens(active_subject))
            if subj_tokens and any(subj_tokens.intersection(set(_p19p36l_tokens(str(x)))) for x in history or []):
                domain_bonus += 0.18

        final_score = min(1.0, base_score + domain_bonus)

        return {
            "score": round(final_score, 4),
            "query_tokens": sorted(query_tokens),
            "memory_hits": unique_hits,
            "scored_items": scored_items[-8:],
            "confidence": "HIGH" if final_score >= 0.65 else ("MEDIUM" if final_score >= 0.35 else "LOW")
        }
    except Exception as e:
        return {
            "score": 0.0,
            "query_tokens": [],
            "memory_hits": [],
            "scored_items": [],
            "confidence": "ERROR",
            "error": repr(e)
        }

def attach_memory_fusion_shadow(sender: str, text: str, ctx: dict | None = None) -> dict:
    ctx = dict(ctx or {})
    shadow = ctx.get("p19p36k_memory_shadow", {})
    history = shadow.get("history", [])
    scoring = score_memory_relevance(
        text=text,
        history=history,
        active_subject=ctx.get("active_subject") or "",
        active_domain=ctx.get("active_domain") or "",
    )
    ctx["p19p36l_memory_fusion_shadow"] = scoring
    return ctx
# /P19P36L_MEMORY_FUSION_SHADOW_SCORING
