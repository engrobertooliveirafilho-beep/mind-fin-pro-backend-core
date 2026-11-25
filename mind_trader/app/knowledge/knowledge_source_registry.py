import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

ALLOWED_SOURCE_TYPES={"PUBLIC_TEXT","INTERNAL_NOTE","CSV_NOTE","MANUAL_RESEARCH"}

def source_hash(content):
    return hashlib.sha256(str(content).encode("utf-8")).hexdigest()

def register_knowledge_source(name, source_type, content, path="mind_trader/reports/P8.88_knowledge_source_registry.json"):
    if not isinstance(name, str) or not name.strip() or not isinstance(content, str):
        return {"decision":"BLOCK_INVALID_SOURCE","production":"BLOCKED","edge_claim":"NONE"}
    if not isinstance(source_type, str) or source_type not in ALLOWED_SOURCE_TYPES:
        return {"decision":"BLOCK_SOURCE_TYPE","production":"BLOCKED","edge_claim":"NONE"}
    if not str(content).strip():
        return {"decision":"BLOCK_EMPTY_SOURCE","production":"BLOCKED","edge_claim":"NONE"}
    src={
        "source_id":source_hash(name+source_type+content)[:24],
        "name":name,
        "source_type":source_type,
        "content_hash":source_hash(content),
        "registered_at":datetime.now(UTC).isoformat(),
        "status":"REGISTERED_FOR_RESEARCH",
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    try:
        data=json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
        if not isinstance(data, list) or any(not isinstance(x, dict) or not isinstance(x.get("source_id"), str) for x in data):
            raise ValueError("invalid registry")
    except (OSError, ValueError):
        return {"decision":"BLOCK_INVALID_SOURCE_REGISTRY","production":"BLOCKED","edge_claim":"NONE"}
    data=[x for x in data if x["source_id"]!=src["source_id"]]+[src]
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    return src

def require_source_registered(source_id_value,path="mind_trader/reports/P8.88_knowledge_source_registry.json"):
    p=Path(path)
    if not p.exists():
        return {"allowed":False,"decision":"BLOCK_SOURCE_REGISTRY_NOT_FOUND","production":"BLOCKED","edge_claim":"NONE"}
    try:
        data=json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, list) or any(not isinstance(s, dict) or not isinstance(s.get("source_id"), str) or not isinstance(s.get("status"), str) for s in data):
            raise ValueError("invalid registry")
    except (OSError, ValueError):
        return {"allowed":False,"decision":"BLOCK_INVALID_SOURCE_REGISTRY","production":"BLOCKED","edge_claim":"NONE"}
    for s in data:
        if s["source_id"]==source_id_value and s["status"]=="REGISTERED_FOR_RESEARCH":
            return {"allowed":True,"decision":"SOURCE_OK","source":s,"production":"BLOCKED","edge_claim":"NONE"}
    return {"allowed":False,"decision":"BLOCK_SOURCE_NOT_REGISTERED","production":"BLOCKED","edge_claim":"NONE"}
