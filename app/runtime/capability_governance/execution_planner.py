import json
import re
from pathlib import Path

CONTRACTS_PATH = Path("app/runtime/capability_contracts/executable_capability_contracts.json")


STOP = {
    "não","para","como","uma","meu","minha","com","sem","que","dos","das",
    "por","the","and","only","prossiga"
}


def _tokens(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9áéíóúàãõâêôç_]+", " ", text)
    return set(x for x in text.split() if len(x) >= 3 and x not in STOP)


def load_contracts():
    if not CONTRACTS_PATH.exists():
        return {}

    return json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))


def score_contract(query, contract):
    qt = _tokens(query)

    fields = []
    fields.extend(contract.get("can_handle", []))
    fields.extend(contract.get("requires", []))
    fields.extend(contract.get("produces", []))
    fields.append(contract.get("purpose", ""))
    fields.append(contract.get("path", ""))

    ct = _tokens(" ".join(str(x or "") for x in fields))
    overlap = qt.intersection(ct)

    score = 0
    reasons = []

    if overlap:
        score += len(overlap) * 50
        reasons.append("overlap:" + ",".join(sorted(overlap)))

    quality = contract.get("quality", {})
    elapsed = quality.get("elapsed_ms")

    score += min(20, int(quality.get("technical_score") or 0) // 6)

    if isinstance(elapsed, (int, float)) and elapsed > 5000:
        score -= 30
        reasons.append("latency_penalty")

    if not overlap:
        score -= 80
        reasons.append("no_overlap")

    return score, reasons


def plan_capabilities(user_text, context=None, limit=5):
    contracts = load_contracts()

    ranked = []
    rejected = []

    for path, contract in contracts.items():
        score, reasons = score_contract(user_text, contract)

        item = {
            "id": contract.get("id"),
            "path": path,
            "score": score,
            "reasons": reasons,
            "requires": contract.get("requires", []),
            "produces": contract.get("produces", []),
            "can_handle": contract.get("can_handle", [])[:12],
        }

        if score > 0:
            ranked.append(item)
        else:
            rejected.append(item)

    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    steps = []

    for r in ranked[:limit]:
        steps.append({
            "step": len(steps) + 1,
            "type": "capability",
            "id": r["id"],
            "path": r["path"],
            "score": r["score"],
            "requires": r["requires"],
            "produces": r["produces"],
            "reason": r["reasons"],
            "mode": "shadow_only",
        })

    if not steps:
        steps.append({
            "step": 1,
            "type": "knowledge_provider_fallback",
            "reason": "no_safe_executable_capability_matched",
            "mode": "shadow_only",
        })

    steps.append({
        "step": len(steps) + 1,
        "type": "final_answer_governance",
        "reason": "single_final_authority",
        "mode": "shadow_only",
    })

    return {
        "input": user_text,
        "steps": steps,
        "selected_count": len([s for s in steps if s["type"] == "capability"]),
        "rejected_count": len(rejected),
        "mode": "shadow_only",
    }


if __name__ == "__main__":
    tests = [
        "como automatizar confinamento de boi",
        "crie uma estratégia de marketing para eldora",
        "validar runtime trader FTMO paper only",
        "minha Mercedes não entra ré",
        "corrigir resposta do WhatsApp",
        "prossiga",
    ]

    for t in tests:
        print(json.dumps(plan_capabilities(t), indent=2, ensure_ascii=False))
