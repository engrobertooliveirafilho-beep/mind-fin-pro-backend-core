from pathlib import Path
import json
import re

from app.runtime.capability_governance.contract import GovernanceDecision, GovernanceRequest
from app.runtime.capability_governance.loader import load_shadow_capabilities

UNIVERSAL_PATH = Path("app/runtime/capability_profiles/universal_capability_index.json")

def load_index():
    if not UNIVERSAL_PATH.exists():
        return {}
    return json.loads(UNIVERSAL_PATH.read_text(encoding="utf-8"))

def tokens(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9áéíóúàãõâêôç_]+", " ", text)
    return sorted(set(x for x in text.split() if len(x) >= 3))

def score_capability(cap, request: GovernanceRequest, index=None):
    profile = (index or {}).get(cap.path, {})
    query_tokens = set(tokens(request.text))
    capability_tokens = set(profile.get("tokens", []))
    overlap = query_tokens.intersection(capability_tokens)

    score = 0
    reasons = []
    kind = profile.get("execution_kind")

    if kind == "EXECUTABLE_CAPABILITY":
        score += 100
        reasons.append("executable")
    elif kind == "STRUCTURAL_OR_EMPTY":
        score += 20
        reasons.append("structural")
    elif kind == "ROUTE_MODULE":
        score -= 50
        reasons.append("route_penalty")
    elif kind in ["FAILED", "IMPORT_FAILED"]:
        score -= 150
        reasons.append("failed_penalty")

    if overlap:
        score += len(overlap) * 25
        reasons.append("token_overlap:" + ",".join(sorted(overlap)[:10]))

    tech_score = int(profile.get("technical_score", 0))
    score += min(20, tech_score // 6)

    elapsed = profile.get("elapsed_ms")
    if isinstance(elapsed, (int, float)) and elapsed > 5000:
        score -= 20
        reasons.append("latency_penalty")

    if not overlap and kind != "EXECUTABLE_CAPABILITY":
        score -= 30
        reasons.append("no_overlap_non_executable_penalty")

    return score, reasons

def decide(request: GovernanceRequest, limit: int = 5):
    capabilities = load_shadow_capabilities()
    index = load_index()

    ranked = []
    rejected = []

    for cap in capabilities:
        score, reasons = score_capability(cap, request, index)
        item = {
            "id": cap.id,
            "name": cap.name,
            "path": cap.path,
            "score": score,
            "reasons": reasons,
        }

        if score > 0:
            ranked.append((score, cap, reasons))
        else:
            rejected.append(item)

    ranked.sort(key=lambda x: x[0], reverse=True)

    return GovernanceDecision(
        selected=[x[1] for x in ranked[:limit]],
        rejected=rejected,
        reason="universal_capability_discovery_selector",
        mode="shadow",
    )

def infer_domain(text: str):
    return "universal"
