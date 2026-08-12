from pathlib import Path

p = Path("app/companionship/safe_recovery_adapter.py")
s = p.read_text(encoding="utf-8")

insert = r'''

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
'''

if "P19P36M_H2_DOMAIN_SEMANTIC_MEMORY_BRIDGE" not in s:
    s += insert

old = '''        final_score = min(1.0, base_score + domain_bonus)

        return {
            "score": round(final_score, 4),
            "query_tokens": sorted(query_tokens),
            "memory_hits": unique_hits,
            "scored_items": scored_items[-8:],
            "confidence": "HIGH" if final_score >= 0.65 else ("MEDIUM" if final_score >= 0.35 else "LOW")
        }
'''

new = '''        bridge = _p19p36m_h2_domain_semantic_bridge(text, history, active_domain, active_subject)
        bridge_bonus = 0.62 if bridge.get("matched") else 0.0

        final_score = min(1.0, base_score + domain_bonus + bridge_bonus)

        if bridge.get("matched"):
            for h in bridge.get("memory_hits", []):
                if h not in unique_hits:
                    unique_hits.append(h)
            if not scored_items:
                for item in history[-5:]:
                    scored_items.append({
                        "text": str(item)[:240],
                        "overlap": bridge.get("memory_hits", [])[:6],
                        "score": bridge_bonus
                    })

        return {
            "score": round(final_score, 4),
            "query_tokens": sorted(query_tokens),
            "memory_hits": sorted(set(unique_hits)),
            "scored_items": scored_items[-8:],
            "domain_semantic_bridge": bridge,
            "confidence": "HIGH" if final_score >= 0.65 else ("MEDIUM" if final_score >= 0.35 else "LOW")
        }
'''

if "domain_semantic_bridge" not in s:
    if old not in s:
        raise SystemExit("score return block not found")
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("P19P36M_H2_DOMAIN_BRIDGE_PATCH_OK")
