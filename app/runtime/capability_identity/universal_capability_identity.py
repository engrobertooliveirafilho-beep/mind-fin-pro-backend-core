from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

ROOT = Path.cwd()
MODE = "SHADOW_ONLY"

SOURCES = {
    "shadow_registry": ROOT / "app/runtime/shadow_registry/registry.json",
    "capability_descriptors": ROOT / "app/runtime/capability_descriptors/capability_runtime_descriptors.json",
    "semantic_contracts": ROOT / "app/runtime/capability_contracts/capability_semantic_contracts.json",
    "capability_graph": ROOT / "app/runtime/capability_graph/capability_knowledge_graph.json",
    "capability_abstraction": ROOT / "app/runtime/capability_abstraction/capability_abstraction_layer.json",
}

def _load(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def _norm_key(value: str) -> str:
    v = str(value or "").replace("\\", "/").lower().strip()
    v = re.sub(r"\.py$", "", v)
    v = v.replace("/", ".")
    v = re.sub(r"^app\.", "app.", v)
    return v

def _slug(value: str) -> str:
    v = _norm_key(value)
    v = v.split(".")[-1]
    v = re.sub(r"[^a-z0-9]+", "_", v).strip("_")
    return v or "unknown"

def _records(data: Any):
    if isinstance(data, dict) and isinstance(data.get("capabilities"), list):
        data = data["capabilities"]

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item
        return

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                item = dict(v)
                item.setdefault("_key", k)
                yield item

def _candidate_keys(item: Dict[str, Any]):
    keys = []
    for field in ["file", "path", "module", "id", "_key"]:
        if item.get(field):
            keys.append(str(item[field]))

    for field in ["file", "path"]:
        if item.get(field):
            keys.append(str(item[field]).replace("/", ".").replace("\\", ".").replace(".py", ""))

    return sorted(set(_norm_key(k) for k in keys if k))

def build_identity_map() -> Dict[str, Any]:
    raw_items = []

    for source_name, path in SOURCES.items():
        data = _load(path)
        for item in _records(data):
            keys = _candidate_keys(item)
            if not keys:
                continue

            primary = None
            for k in keys:
                if k.startswith("app."):
                    primary = k
                    break
            primary = primary or keys[0]

            raw_items.append({
                "source": source_name,
                "primary": primary,
                "keys": keys,
                "item": item,
            })

    groups: Dict[str, Dict[str, Any]] = {}

    for r in raw_items:
        slug = _slug(r["primary"])

        if slug not in groups:
            groups[slug] = {
                "uid": f"CAP_{slug.upper()}",
                "slug": slug,
                "canonical_module": None,
                "canonical_file": None,
                "aliases": set(),
                "sources": set(),
                "evidence_count": 0,
            }

        g = groups[slug]
        g["sources"].add(r["source"])
        g["evidence_count"] += 1

        for k in r["keys"]:
            g["aliases"].add(k)

        for k in r["keys"]:
            if k.startswith("app."):
                g["canonical_module"] = g["canonical_module"] or k
                g["canonical_file"] = g["canonical_file"] or (k.replace(".", "/") + ".py")

    capabilities = []
    alias_index = {}

    for slug, g in sorted(groups.items()):
        record = {
            "uid": g["uid"],
            "slug": g["slug"],
            "canonical_module": g["canonical_module"],
            "canonical_file": g["canonical_file"],
            "aliases": sorted(g["aliases"]),
            "sources": sorted(g["sources"]),
            "evidence_count": g["evidence_count"],
            "mode": MODE,
            "production_allowed": False,
        }

        capabilities.append(record)

        for a in record["aliases"]:
            alias_index[a] = record["uid"]

    return {
        "mode": MODE,
        "capability_count": len(capabilities),
        "capabilities": capabilities,
        "alias_index": alias_index,
        "production_allowed": False,
        "shadow_only": True,
    }

def resolve_capability(value: str) -> Dict[str, Any]:
    identity = build_identity_map()
    key = _norm_key(value)
    uid = identity["alias_index"].get(key)

    if not uid:
        slug = _slug(value)
        uid = f"CAP_{slug.upper()}"

    hit = next((x for x in identity["capabilities"] if x["uid"] == uid), None)

    return {
        "query": value,
        "normalized": key,
        "uid": uid,
        "found": hit is not None,
        "capability": hit,
        "mode": MODE,
        "production_allowed": False,
    }

if __name__ == "__main__":
    identity = build_identity_map()
    print(json.dumps({
        "mode": identity["mode"],
        "capability_count": identity["capability_count"],
        "production_allowed": identity["production_allowed"],
        "sample": identity["capabilities"][:10],
    }, indent=2, ensure_ascii=False))

    for q in [
        "app/api/eldora_semantic.py",
        "app.api.eldora_semantic",
        "011_eldora_semantic",
        "eldora_semantic",
    ]:
        print(json.dumps(resolve_capability(q), indent=2, ensure_ascii=False))
