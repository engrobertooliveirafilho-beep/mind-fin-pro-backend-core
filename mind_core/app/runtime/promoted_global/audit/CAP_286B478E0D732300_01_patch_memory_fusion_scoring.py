from pathlib import Path

p = Path("app/companionship/safe_recovery_adapter.py")
s = p.read_text(encoding="utf-8")

insert = r'''

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
'''

if "P19P36L_MEMORY_FUSION_SHADOW_SCORING" not in s:
    s += insert

old = '''    try:
        ctx = collect_memory_shadow(sender, text, ctx)
    except Exception:
        pass
    recovered: List[Dict[str, Any]] = []
'''

new = '''    try:
        ctx = collect_memory_shadow(sender, text, ctx)
    except Exception:
        pass
    try:
        ctx = attach_memory_fusion_shadow(sender, text, ctx)
    except Exception:
        pass
    recovered: List[Dict[str, Any]] = []
'''

if "attach_memory_fusion_shadow(sender, text, ctx)" not in s:
    if old not in s:
        raise SystemExit("collect_memory_shadow insertion block not found")
    s = s.replace(old, new, 1)

old2 = '''            "memory_shadow": (ctx or {}).get("p19p36k_memory_shadow", {}),
            "reply_preview": (reply or "")[:300],
'''

new2 = '''            "memory_shadow": (ctx or {}).get("p19p36k_memory_shadow", {}),
            "memory_fusion_shadow": (ctx or {}).get("p19p36l_memory_fusion_shadow", {}),
            "reply_preview": (reply or "")[:300],
'''

if '"memory_fusion_shadow": (ctx or {}).get("p19p36l_memory_fusion_shadow", {}),' not in s:
    if old2 not in s:
        raise SystemExit("telemetry memory_shadow block not found")
    s = s.replace(old2, new2, 1)

p.write_text(s, encoding="utf-8")
print("P19P36L_MEMORY_FUSION_SCORING_PATCH_OK")
