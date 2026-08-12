import json
from pathlib import Path

ROOT = Path.cwd()
REGISTRY = ROOT / "app" / "runtime" / "shadow_registry" / "registry.json"
BACKUP = REGISTRY.with_suffix(".json.bak_mind_os_1b")

DOMAIN_RULES = {
    "whatsapp": ["whatsapp", "twilio", "webhook", "message", "conversation", "reply"],
    "trader": ["trader", "trade", "ftmo", "market", "signal", "backtest", "broker", "order"],
    "marketing": ["marketing", "copy", "social", "instagram", "tiktok", "creative", "campaign"],
    "agro": ["agro", "boi", "gado", "confinamento", "farm", "pecuaria"],
    "automotive": ["mercedes", "aks", "car", "vehicle", "auto", "gear", "clutch"],
    "memory": ["memory", "context", "state", "history", "recall"],
    "retrieval": ["retrieval", "search", "embedding", "vector", "knowledge"],
    "runtime": ["runtime", "router", "orchestrator", "pipeline", "engine"],
    "api": ["api", "route", "endpoint", "server"],
}

def infer_domains(text):
    low = text.lower()
    found = []
    for domain, keys in DOMAIN_RULES.items():
        if any(k in low for k in keys):
            found.append(domain)
    return found or ["general"]

def infer_intents(text):
    low = text.lower()
    intents = []

    if any(k in low for k in ["classify", "classifier"]):
        intents.append("classify")
    if any(k in low for k in ["route", "router"]):
        intents.append("route")
    if any(k in low for k in ["generate", "answer", "reply", "response"]):
        intents.append("generate")
    if any(k in low for k in ["analyze", "audit", "trace", "debug"]):
        intents.append("analyze")
    if any(k in low for k in ["search", "retrieval", "lookup"]):
        intents.append("retrieve")
    if any(k in low for k in ["memory", "context", "state"]):
        intents.append("remember")

    return intents or ["assist"]

def normalize_items(raw):
    if isinstance(raw, dict):
        key = "capabilities" if "capabilities" in raw else "items" if "items" in raw else "registry" if "registry" in raw else None
        items = raw[key] if key else []
        return raw, key, items

    if isinstance(raw, list):
        return {"capabilities": raw}, "capabilities", raw

    raise TypeError("registry format not supported")

def main():
    raw = json.loads(REGISTRY.read_text(encoding="utf-8"))
    REGISTRY.replace(BACKUP)

    root, key, items = normalize_items(raw)

    enriched = []

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue

        blob = " ".join(str(item.get(k, "")) for k in ["id", "name", "path", "file", "module_path", "description"])

        item["domains"] = item.get("domains") or item.get("domain") or infer_domains(blob)
        item["intents"] = item.get("intents") or item.get("intent") or infer_intents(blob)
        item["mode"] = item.get("mode") or "shadow"
        item["priority"] = int(item.get("priority") or 1)
        item["confidence"] = float(item.get("confidence") or 0.25)
        item["health"] = item.get("health") or item.get("status") or "ACTIVE_CAPABILITY"

        if isinstance(item["domains"], str):
            item["domains"] = [item["domains"]]

        if isinstance(item["intents"], str):
            item["intents"] = [item["intents"]]

        enriched.append(item)

    root[key] = enriched
    REGISTRY.write_text(json.dumps(root, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "registry": str(REGISTRY),
        "backup": str(BACKUP),
        "total": len(enriched),
        "with_domains": sum(1 for x in enriched if x.get("domains")),
        "with_intents": sum(1 for x in enriched if x.get("intents")),
        "shadow": sum(1 for x in enriched if x.get("mode") == "shadow"),
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
