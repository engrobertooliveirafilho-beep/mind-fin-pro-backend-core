from pathlib import Path

p = Path("app/companionship/safe_recovery_adapter.py")
s = p.read_text(encoding="utf-8")

insert = r'''

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

    return advisor

def attach_memory_fusion_advisor_shadow(ctx: dict | None = None) -> dict:
    ctx = dict(ctx or {})
    ctx["p19p36m_memory_fusion_advisor_shadow"] = build_memory_fusion_advisor(ctx)
    return ctx
# /P19P36M_MEMORY_FUSION_ADVISOR_SHADOW
'''

if "P19P36M_MEMORY_FUSION_ADVISOR_SHADOW" not in s:
    s += insert

old = '''    try:
        ctx = attach_memory_fusion_shadow(sender, text, ctx)
    except Exception:
        pass
    recovered: List[Dict[str, Any]] = []
'''

new = '''    try:
        ctx = attach_memory_fusion_shadow(sender, text, ctx)
    except Exception:
        pass
    try:
        ctx = attach_memory_fusion_advisor_shadow(ctx)
    except Exception:
        pass
    recovered: List[Dict[str, Any]] = []
'''

if "attach_memory_fusion_advisor_shadow(ctx)" not in s:
    if old not in s:
        raise SystemExit("attach_memory_fusion_shadow block not found")
    s = s.replace(old, new, 1)

old2 = '''            "memory_fusion_shadow": (ctx or {}).get("p19p36l_memory_fusion_shadow", {}),
            "reply_preview": (reply or "")[:300],
'''

new2 = '''            "memory_fusion_shadow": (ctx or {}).get("p19p36l_memory_fusion_shadow", {}),
            "memory_fusion_advisor_shadow": (ctx or {}).get("p19p36m_memory_fusion_advisor_shadow", {}),
            "reply_preview": (reply or "")[:300],
'''

if '"memory_fusion_advisor_shadow": (ctx or {}).get("p19p36m_memory_fusion_advisor_shadow", {}),' not in s:
    if old2 not in s:
        raise SystemExit("telemetry memory_fusion_shadow block not found")
    s = s.replace(old2, new2, 1)

p.write_text(s, encoding="utf-8")
print("P19P36M_MEMORY_FUSION_ADVISOR_PATCH_OK")
