
import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).with_name("registry.json")


def load_shadow_registry():
    if not REGISTRY_PATH.exists():
        return []
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def list_shadow_capabilities():
    return [
        item for item in load_shadow_registry()
        if item.get("enabled") is True and item.get("production_allowed") is False
    ]


def list_production_allowed():
    return [
        item for item in load_shadow_registry()
        if item.get("production_allowed") is True
    ]
