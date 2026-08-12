import json
from pathlib import Path
from app.runtime.capability_governance.contract import CapabilityDescriptor

ROOT = Path.cwd()
REGISTRY = ROOT / "app" / "runtime" / "shadow_registry" / "registry.json"

def load_shadow_capabilities():
    if not REGISTRY.exists():
        return []

    raw = json.loads(REGISTRY.read_text(encoding="utf-8"))

    if isinstance(raw, dict):
        items = raw.get("capabilities") or raw.get("items") or raw.get("registry") or []
    else:
        items = raw

    capabilities = []

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue

        domains = item.get("domains") or item.get("domain") or []
        intents = item.get("intents") or item.get("intent") or []

        if isinstance(domains, str):
            domains = [domains]
        if isinstance(intents, str):
            intents = [intents]

        capabilities.append(
            CapabilityDescriptor(
                id=str(item.get("id") or item.get("name") or f"capability_{idx}"),
                name=str(item.get("name") or item.get("id") or f"capability_{idx}"),
                path=str(item.get("path") or item.get("file") or item.get("module_path") or ""),
                domains=domains,
                intents=intents,
                mode=str(item.get("mode") or "shadow"),
                priority=int(item.get("priority") or 0),
                confidence=float(item.get("confidence") or 0.0),
                health=str(item.get("health") or "unknown"),
                produces=item.get("produces") or [],
                requires=item.get("requires") or [],
            )
        )

    return capabilities
