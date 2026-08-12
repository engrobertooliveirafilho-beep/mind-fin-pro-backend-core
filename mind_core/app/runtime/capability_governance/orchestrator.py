import json
from pathlib import Path

from app.runtime.capability_governance.goal_intent_graph import infer_goal_intent

CAL_PATH = Path("app/runtime/capability_abstraction/capability_abstraction_layer.json")
KP_DIR = Path("app/runtime/knowledge_providers")

def load_cal():
    if not CAL_PATH.exists():
        return {}
    return json.loads(CAL_PATH.read_text(encoding="utf-8"))

def classify_request_flags(goal_graph):
    t = set(goal_graph.get("tokens", []))
    flags = set()

    if {"trade", "trader", "ftmo", "mercado", "backtest"} & t:
        flags.add("financial_trading_execution")
    if {"mercedes", "aks", "carro", "cambio", "câmbio", "embreagem", "entra"} & t:
        flags.add("vehicle_diagnostics_execution")
    if {"boi", "gado", "confinamento", "fazenda", "agro"} & t:
        flags.add("agriculture_operations_execution")

    return sorted(flags)

def available_knowledge_provider(goal_graph):
    tokens = set(goal_graph.get("tokens", []))
    intent = str(goal_graph.get("intent", "")).lower()
    outputs = set(goal_graph.get("required_outputs", []))
    required = set(goal_graph.get("required_capabilities", []))

    if not KP_DIR.exists():
        return None

    candidates = []

    for p in KP_DIR.glob("*.py"):
        name = p.stem.lower()
        if name.startswith("_") or name == "contract":
            continue

        text = p.read_text(encoding="utf-8", errors="ignore").lower()
        blob = name + " " + text[:12000]

        score = 0
        hits = []

        for t in tokens:
            if t in blob:
                score += 20
                hits.append(t)

        for out in outputs:
            if out.lower() in blob:
                score += 10
                hits.append("output:" + out)

        for req in required:
            if req.lower() in blob:
                score += 15
                hits.append("required:" + req)

        if intent and intent in blob:
            score += 20
            hits.append("intent:" + intent)

        if name == "universal_knowledge_provider":
            score += 55
            hits.append("universal_provider_bonus")

        if "legacy" in name:
            score -= 80
            hits.append("legacy_penalty")

        if score >= 40:
            candidates.append({
                "provider": name,
                "path": str(p).replace("\\", "/"),
                "score": score,
                "hits": sorted(set(hits))
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)

    return candidates[0] if candidates else None

def map_required_to_abstract(required):
    mapping = {
        "memory": "memory",
        "knowledge_provider": "knowledge_provider",
        "planner": "routing",
        "generation": "generation",
        "diagnostic": "diagnostic",
        "quality_guard": "quality_guard",
        "naturalizer": "generation",
        "governance": "final_authority",
        "final_answer_governance": "final_authority",
    }

    out = []
    for r in required:
        v = mapping.get(r)
        if v and v not in out:
            out.append(v)

    return out

def choose_implementation(abstract_name, cal, request_flags):
    node = cal.get(abstract_name)
    if not node:
        return None, "missing_abstract_capability"

    for impl in node.get("implementations", []):
        blocked = set(impl.get("never_use_for", [])) & set(request_flags)

        if blocked:
            continue

        if impl.get("mode") != "shadow_only":
            continue

        return impl, "selected"

    return None, "no_allowed_implementation"

def build_orchestration_plan(text, context=None):
    goal_graph = infer_goal_intent(text)
    request_flags = classify_request_flags(goal_graph)
    cal = load_cal()

    required = goal_graph.get("required_capabilities", [])
    abstract_chain = map_required_to_abstract(required)

    steps = []
    rejected = []

    kp = available_knowledge_provider(goal_graph)

    for abstract_name in abstract_chain:
        if abstract_name == "knowledge_provider":
            if kp:
                steps.append({
                    "step": len(steps) + 1,
                    "type": "knowledge_provider",
                    "abstract_capability": "knowledge_provider",
                    "provider": kp["provider"],
                    "path": kp["path"],
                    "score": kp["score"],
                    "reason": "matched_existing_provider",
                    "mode": "shadow_only",
                })
            else:
                steps.append({
                    "step": len(steps) + 1,
                    "type": "knowledge_provider_fallback",
                    "abstract_capability": "knowledge_provider",
                    "reason": "no_specific_provider_available",
                    "mode": "shadow_only",
                })
            continue

        impl, reason = choose_implementation(abstract_name, cal, request_flags)

        if impl:
            steps.append({
                "step": len(steps) + 1,
                "type": "capability",
                "abstract_capability": abstract_name,
                "id": impl.get("id"),
                "path": impl.get("path"),
                "score": impl.get("score"),
                "reason": reason,
                "mode": "shadow_only",
            })
        else:
            rejected.append({
                "abstract_capability": abstract_name,
                "reason": reason
            })

    if not steps:
        steps.append({
            "step": 1,
            "type": "knowledge_provider_fallback",
            "reason": "no_provider_and_no_capability_available",
            "mode": "shadow_only",
        })

    steps.append({
        "step": len(steps) + 1,
        "type": "final_answer_governance",
        "reason": "single_final_authority",
        "mode": "shadow_only",
    })

    return {
        "input": text,
        "goal_graph": goal_graph,
        "request_flags": request_flags,
        "abstract_chain": abstract_chain,
        "knowledge_provider": kp,
        "steps": steps,
        "selected_count": len([x for x in steps if x["type"] == "capability"]),
        "rejected": rejected,
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
        print(json.dumps(build_orchestration_plan(t), indent=2, ensure_ascii=False))
