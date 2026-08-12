from pathlib import Path

p = Path("app/companionship/safe_recovery_adapter.py")
s = p.read_text(encoding="utf-8")

insert = r'''

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
'''

if "P19P36M_H3_AUTHORITATIVE_MEMORY_SCORER_OVERRIDE" not in s:
    s += insert

p.write_text(s, encoding="utf-8")
print("P19P36M_H3_AUTHORITATIVE_SCORER_PATCH_OK")
