from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.runtime.capability_governance.capability_composer import compose_capabilities

ROOT = Path.cwd()
MODE = "SHADOW_ONLY"

SOURCES = {
    "shadow_registry": ROOT / "app/runtime/shadow_registry/registry.json",
    "capability_descriptors": ROOT / "app/runtime/capability_descriptors/capability_runtime_descriptors.json",
    "semantic_contracts": ROOT / "app/runtime/capability_contracts/capability_semantic_contracts.json",
    "capability_graph": ROOT / "app/runtime/capability_graph/capability_knowledge_graph.json",
    "capability_abstraction": ROOT / "app/runtime/capability_abstraction/capability_abstraction_layer.json",
}

def _load_json(path: Path) -> Any:
    if not path.exists():
        return {"_missing": True, "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_error": f"{type(exc).__name__}:{exc}", "path": str(path)}

def _count(data: Any) -> int:
    if isinstance(data, dict):
        if isinstance(data.get("capabilities"), list):
            return len(data["capabilities"])
        return len(data)
    if isinstance(data, list):
        return len(data)
    return 0

def _index_by_path(data: Any) -> Dict[str, Any]:
    out = {}

    if isinstance(data, dict) and isinstance(data.get("capabilities"), list):
        data = data["capabilities"]

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                key = item.get("file") or item.get("path") or item.get("module") or item.get("id")
                if key:
                    out[str(key).replace("\\", "/")] = item
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                key = v.get("file") or v.get("path") or k
                out[str(key).replace("\\", "/")] = v
            else:
                out[str(k).replace("\\", "/")] = v

    return out

def fuse_knowledge(query: str) -> Dict[str, Any]:
    composer = compose_capabilities(query)

    loaded = {name: _load_json(path) for name, path in SOURCES.items()}
    indexes = {name: _index_by_path(data) for name, data in loaded.items()}

    fused_steps: List[Dict[str, Any]] = []

    for step in composer["capability_chain"]:
        file = step["file"].replace("\\", "/")
        module = step["module"]

        evidence = {}
        for source_name, idx in indexes.items():
            hit = None

            if file in idx:
                hit = idx[file]
            elif module in idx:
                hit = idx[module]
            else:
                for k, v in idx.items():
                    if file in k or module in k:
                        hit = v
                        break

            evidence[source_name] = {
                "found": hit is not None,
                "preview": str(hit)[:500] if hit is not None else None,
            }

        fused_steps.append({
            **step,
            "knowledge_evidence": evidence,
            "fusion_status": "FUSED_SHADOW_EVIDENCE",
        })

    source_summary = {
        name: {
            "path": str(SOURCES[name]),
            "count": _count(data),
            "available": not (isinstance(data, dict) and data.get("_missing")),
            "error": data.get("_error") if isinstance(data, dict) else None,
        }
        for name, data in loaded.items()
    }

    return {
        "mode": MODE,
        "query": query,
        "intent": composer["intent"],
        "chain_length": composer["chain_length"],
        "source_summary": source_summary,
        "fused_capability_chain": fused_steps,
        "final_authority_required": True,
        "execution_allowed": False,
        "production_allowed": False,
        "shadow_only": True,
    }

if __name__ == "__main__":
    tests = [
        "como automatizar confinamento de boi",
        "crie estratégia de marketing para eldora",
        "validar runtime trader FTMO paper only",
        "prossiga",
    ]

    for t in tests:
        print(json.dumps(fuse_knowledge(t), indent=2, ensure_ascii=False))
