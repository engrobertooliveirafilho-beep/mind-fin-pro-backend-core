from __future__ import annotations

import importlib
from typing import Any, Dict, List

# P19P36O_B_RELATIONSHIP_MEMORY_SHADOW_WIRING
try:
    from app.companionship.relationship_memory_store import update_relationship_memory_shadow, attach_relationship_memory_advisor_shadow
except Exception:
    update_relationship_memory_shadow = None
    attach_relationship_memory_advisor_shadow = None
# /P19P36O_B_RELATIONSHIP_MEMORY_SHADOW_WIRING

# P19P36P_B_GOAL_TRACKER_SHADOW_WIRING
try:
    from app.companionship.long_term_goal_tracker import update_goal_tracker_from_relationship_profile
except Exception:
    update_goal_tracker_from_relationship_profile = None
# /P19P36P_B_GOAL_TRACKER_SHADOW_WIRING

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
    try:
        ctx = attach_memory_fusion_advisor_shadow(ctx)
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

    try:
        if update_relationship_memory_shadow:
            ctx["p19p36o_relationship_memory_shadow"] = update_relationship_memory_shadow(sender, text)
    except Exception:
        pass
    try:
        if attach_relationship_memory_advisor_shadow:
            ctx = attach_relationship_memory_advisor_shadow(ctx, sender=sender, text=text)
    except Exception:
        pass
    try:
        if update_goal_tracker_from_relationship_profile:
            rel_shadow = ctx.get("p19p36o_relationship_memory_shadow", {}) or {}
            profile = rel_shadow.get("profile", {}) or {}
            ctx["p19p36p_long_term_goal_shadow"] = update_goal_tracker_from_relationship_profile(sender, profile, text=text)
    except Exception:
        pass
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
            "memory_fusion_advisor_shadow": (ctx or {}).get("p19p36m_memory_fusion_advisor_shadow", {}),
            "relationship_memory_shadow": (ctx or {}).get("p19p36o_relationship_memory_shadow", {}),
            "relationship_memory_advisor_shadow": (ctx or {}).get("p19p36o_relationship_memory_advisor_shadow", {}),
            "long_term_goal_shadow": (ctx or {}).get("p19p36p_long_term_goal_shadow", {}),
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
    scoring_history = _p19p36m_hotfix_without_current_message(history, text)
    scoring = score_memory_relevance(
        text=text,
        history=scoring_history,
        active_subject=ctx.get("active_subject") or "",
        active_domain=ctx.get("active_domain") or "",
    )
    scoring["scoring_history_count"] = len(scoring_history)
    scoring["current_message_excluded"] = len(scoring_history) != len(history)
    ctx["p19p36l_memory_fusion_shadow"] = scoring
    return ctx
# /P19P36L_MEMORY_FUSION_SHADOW_SCORING


# P19P36M_MEMORY_FUSION_ADVISOR_SHADOW
def build_memory_fusion_advisor(ctx: dict | None = None) -> dict:
    ctx = dict(ctx or {})
    fusion = ctx.get("p19p36l_memory_fusion_shadow", {}) or {}
    memory = ctx.get("p19p36k_memory_shadow", {}) or {}

    score = float(fusion.get("score") or 0.0)
    confidence = fusion.get("confidence") or "LOW"
    hits = fusion.get("memory_hits") or []
    scored_items = fusion.get("scored_items") or []
    history = memory.get("history") or []

    should_use = bool(score >= 0.55 and hits and history)

    reason = "LOW_RELEVANCE"
    if should_use:
        reason = "Relevant memory detected: " + ", ".join(hits[:6])
    elif score >= 0.35:
        reason = "Medium relevance, keep as shadow only"
    elif not history:
        reason = "No sender history available"
    elif not hits:
        reason = "No semantic overlap with current message"

    recommended = []
    for item in scored_items:
        txt = item.get("text")
        if txt and txt not in recommended:
            recommended.append(txt)
    if not recommended and should_use:
        recommended = history[-3:]

    advisor = {
        "should_use_memory": should_use,
        "memory_score": round(score, 4),
        "confidence": confidence,
        "reason": reason,
        "memory_hits": hits[:12],
        "recommended_memories": recommended[-5:],
        "history_count": len(history),
    }

    return _p19p36m_h4_authoritative_advisor_guard(advisor)

def attach_memory_fusion_advisor_shadow(ctx: dict | None = None) -> dict:
    ctx = dict(ctx or {})
    ctx["p19p36m_memory_fusion_advisor_shadow"] = build_memory_fusion_advisor(ctx)
    return ctx
# /P19P36M_MEMORY_FUSION_ADVISOR_SHADOW


# P19P36M_HOTFIX_EXCLUDE_CURRENT_MESSAGE_FROM_SCORING
def _p19p36m_hotfix_without_current_message(history: list, current_text: str):
    try:
        cur = str(current_text or "").strip().lower()
        if not cur:
            return list(history or [])
        cleaned = []
        removed = False
        for item in history or []:
            val = str(item or "").strip()
            if not removed and val.lower() == cur:
                removed = True
                continue
            cleaned.append(item)
        return cleaned
    except Exception:
        return list(history or [])
# /P19P36M_HOTFIX_EXCLUDE_CURRENT_MESSAGE_FROM_SCORING


# P19P36M_H2_DOMAIN_SEMANTIC_MEMORY_BRIDGE
_P19P36M_H2_DOMAIN_MEMORY_TERMS = {
    "fitness": {
        "memory": {
            "emagrecer", "emagrecimento", "peso", "treino", "treinar", "cardio",
            "joelho", "ombro", "cotovelo", "coluna", "dor", "lesao", "lesão",
            "dieta", "musculacao", "musculação", "exercicio", "exercício",
            "exercicios", "exercícios"
        },
        "query": {
            "quais", "qual", "exercicio", "exercício", "exercicios", "exercícios",
            "treino", "treinar", "cardio", "dieta", "prossiga", "continue",
            "como", "fazer", "plano"
        }
    },
    "trader": {
        "memory": {
            "ftmo", "trader", "trade", "backtest", "risco", "timeframe",
            "estrategia", "estratégia", "stop", "alvo", "mind"
        },
        "query": {
            "continue", "prossiga", "quais", "risco", "entrada", "operar",
            "backtest", "timeframe", "estrategia", "estratégia"
        }
    }
}

def _p19p36m_h2_domain_semantic_bridge(text: str, history: list, active_domain: str = "", active_subject: str = "") -> dict:
    try:
        domain = str(active_domain or "").lower().strip()
        bridge = _P19P36M_H2_DOMAIN_MEMORY_TERMS.get(domain)
        if not bridge:
            return {"matched": False, "domain": domain, "hits": [], "reason": "NO_DOMAIN_BRIDGE"}

        query_text = " ".join([str(text or ""), str(active_subject or "")]).lower()
        hist_text = " ".join([str(x or "") for x in history or []]).lower()

        query_hits = sorted([x for x in bridge["query"] if x in query_text])
        memory_hits = sorted([x for x in bridge["memory"] if x in hist_text])

        matched = bool(query_hits and memory_hits)

        return {
            "matched": matched,
            "domain": domain,
            "query_hits": query_hits[:12],
            "memory_hits": memory_hits[:12],
            "reason": "DOMAIN_SEMANTIC_BRIDGE" if matched else "NO_DOMAIN_SEMANTIC_MATCH"
        }
    except Exception as e:
        return {"matched": False, "domain": active_domain or "", "hits": [], "reason": "ERROR", "error": repr(e)}
# /P19P36M_H2_DOMAIN_SEMANTIC_MEMORY_BRIDGE


# P19P36M_H3_AUTHORITATIVE_MEMORY_SCORER_OVERRIDE
def score_memory_relevance(text: str, history: list, active_subject: str = "", active_domain: str = "") -> dict:
    """
    Authoritative scorer.
    Rules:
    - Never scores current message against itself.
    - Always returns domain_semantic_bridge.
    - Uses direct token overlap + domain semantic bridge.
    - Does not mutate reply.
    """
    try:
        clean_history = _p19p36m_hotfix_without_current_message(history or [], text)

        query_tokens = set(_p19p36l_tokens(" ".join([
            text or "",
            active_subject or "",
            active_domain or ""
        ])))

        hits = []
        scored_items = []

        for item in clean_history:
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

        domain_bonus = 0.0
        hist_joined = " ".join([str(x).lower() for x in clean_history])
        if active_domain and str(active_domain).lower() in hist_joined:
            domain_bonus += 0.12

        subj_tokens = set(_p19p36l_tokens(active_subject or ""))
        if subj_tokens:
            for item in clean_history:
                if subj_tokens.intersection(set(_p19p36l_tokens(str(item)))):
                    domain_bonus += 0.18
                    break

        bridge = _p19p36m_h2_domain_semantic_bridge(
            text=text,
            history=clean_history,
            active_domain=active_domain,
            active_subject=active_subject,
        )

        bridge_bonus = 0.70 if bridge.get("matched") else 0.0

        if bridge.get("matched"):
            for h in bridge.get("memory_hits", []):
                if h not in unique_hits:
                    unique_hits.append(h)

            if not scored_items:
                for item in clean_history[-5:]:
                    scored_items.append({
                        "text": str(item)[:240],
                        "overlap": bridge.get("memory_hits", [])[:8],
                        "score": bridge_bonus
                    })

        final_score = min(1.0, base_score + domain_bonus + bridge_bonus)

        return {
            "score": round(final_score, 4),
            "query_tokens": sorted(query_tokens),
            "memory_hits": sorted(set(unique_hits)),
            "scored_items": scored_items[-8:],
            "domain_semantic_bridge": bridge,
            "confidence": "HIGH" if final_score >= 0.65 else ("MEDIUM" if final_score >= 0.35 else "LOW"),
            "scoring_history_count": len(clean_history),
            "current_message_excluded": len(clean_history) != len(history or []),
            "scorer_version": "P19P36M_H3_AUTHORITATIVE"
        }
    except Exception as e:
        return {
            "score": 0.0,
            "query_tokens": [],
            "memory_hits": [],
            "scored_items": [],
            "domain_semantic_bridge": {"matched": False, "reason": "ERROR"},
            "confidence": "ERROR",
            "scoring_history_count": 0,
            "current_message_excluded": False,
            "scorer_version": "P19P36M_H3_AUTHORITATIVE",
            "error": repr(e)
        }
# /P19P36M_H3_AUTHORITATIVE_MEMORY_SCORER_OVERRIDE

# ---------------------------------------------------------------------
# P19P36M-H4 AUTHORITATIVE ADVISOR GUARD
# Regra: memória só pode ser ativada se existir evidência positiva real.
# Proíbe should_use_memory=True quando score=0, memory_hits=[], bridge=False.
# ---------------------------------------------------------------------
def _p19p36m_h4_authoritative_advisor_guard(advisor: dict) -> dict:
    if not isinstance(advisor, dict):
        return {
            "should_use_memory": False,
            "memory_score": 0.0,
            "recommended_memories": [],
            "reason": "P19P36M_H4_INVALID_ADVISOR_OBJECT",
            "advisor_guard_version": "P19P36M_H4_AUTHORITATIVE"
        }

    score = float(
        advisor.get("memory_score",
        advisor.get("score", 0.0)) or 0.0
    )

    hits = advisor.get("memory_hits", [])
    recommended = advisor.get("recommended_memories", [])
    bridge = bool(
        advisor.get("bridge", False) or
        advisor.get("domain_semantic_bridge", False) or
        advisor.get("semantic_bridge", False)
    )

    has_hits = isinstance(hits, list) and len(hits) > 0
    has_recommended = isinstance(recommended, list) and len(recommended) > 0

    positive_evidence = (
        score > 0.0 and
        (has_hits or has_recommended or bridge)
    )

    advisor["memory_score"] = score
    advisor["should_use_memory"] = bool(positive_evidence)
    advisor["advisor_guard_version"] = "P19P36M_H4_AUTHORITATIVE"
    advisor["advisor_guard_positive_evidence"] = bool(positive_evidence)
    advisor["advisor_guard_inputs"] = {
        "score": score,
        "memory_hits_count": len(hits) if isinstance(hits, list) else 0,
        "recommended_count": len(recommended) if isinstance(recommended, list) else 0,
        "bridge": bridge
    }

    if not positive_evidence:
        advisor["recommended_memories"] = []
        advisor["reason"] = "P19P36M_H4_BLOCKED_NO_POSITIVE_MEMORY_EVIDENCE"

    return advisor

# ---------------------------------------------------------------------
# P19P36N MEMORY FUSION LIVE GATED
# Controlled live memory usage.
# Default OFF unless explicit feature flag is enabled.
# ---------------------------------------------------------------------
import os as _p19p36n_os
import json as _p19p36n_json
from datetime import datetime as _p19p36n_datetime
from pathlib import Path as _p19p36n_Path

_P19P36N_TELEMETRY = _p19p36n_Path("_runtime_state/p19p36n_memory_fusion_live_gated.jsonl")
_P19P36N_TELEMETRY.parent.mkdir(parents=True, exist_ok=True)

def _p19p36n_memory_fusion_enabled() -> bool:
    return str(_p19p36n_os.getenv("P19P36N_MEMORY_FUSION_ENABLED", "false")).lower() in {
        "1", "true", "yes", "on"
    }

def build_memory_fusion_live_context(ctx: dict | None = None) -> dict:
    ctx = dict(ctx or {})
    advisor = ctx.get("p19p36m_memory_fusion_advisor_shadow", {}) or {}

    enabled = _p19p36n_memory_fusion_enabled()
    should_use = bool(advisor.get("should_use_memory") is True)
    score = float(advisor.get("memory_score") or 0.0)
    recommended = advisor.get("recommended_memories") or []

    live_allowed = bool(enabled and should_use and score > 0.0 and recommended)

    live_context = {
        "enabled": enabled,
        "live_allowed": live_allowed,
        "advisor_should_use_memory": should_use,
        "advisor_score": score,
        "recommended_memories": recommended[:5] if isinstance(recommended, list) else [],
        "mode": "LIVE_GATED" if live_allowed else "SHADOW_ONLY",
        "version": "P19P36N_MEMORY_FUSION_LIVE_GATED",
    }

    ctx["p19p36n_memory_fusion_live_context"] = live_context
    return ctx

def attach_memory_fusion_live_gated(ctx: dict | None = None) -> dict:
    return build_memory_fusion_live_context(ctx)

def record_p19p36n_memory_fusion_telemetry(sender: str, text: str, ctx: dict | None, reply_before: str = "", reply_after: str = "") -> None:
    try:
        ctx = dict(ctx or {})
        live = ctx.get("p19p36n_memory_fusion_live_context", {}) or {}
        advisor = ctx.get("p19p36m_memory_fusion_advisor_shadow", {}) or {}

        event = {
            "timestamp": _p19p36n_datetime.utcnow().isoformat() + "Z",
            "sender": sender,
            "text_preview": str(text or "")[:240],
            "enabled": live.get("enabled", False),
            "live_allowed": live.get("live_allowed", False),
            "mode": live.get("mode", "SHADOW_ONLY"),
            "advisor_score": advisor.get("memory_score", 0.0),
            "advisor_should_use_memory": advisor.get("should_use_memory", False),
            "recommended_count": len(live.get("recommended_memories", []) or []),
            "reply_changed": bool((reply_before or "") != (reply_after or "")),
            "version": "P19P36N_MEMORY_FUSION_LIVE_GATED",
        }

        with _P19P36N_TELEMETRY.open("a", encoding="utf-8") as f:
            f.write(_p19p36n_json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass
# /P19P36N_MEMORY_FUSION_LIVE_GATED







