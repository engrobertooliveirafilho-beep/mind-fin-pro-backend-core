import json, hashlib
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.dna.trader_dna_authority import create_dna_atom
from mind_trader.app.knowledge.knowledge_source_registry import require_source_registered

KEYWORDS={
    "liquidity":["liquidity","sweep","stop hunt","absorção","liquidez"],
    "breakout":["breakout","rompimento","expansion","range break"],
    "pullback":["pullback","retest","correction","retorno"],
    "volume":["volume","delta","vwap","profile","absorção"]
}

def source_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]

def classify_text(text):
    t=text.lower()
    scores={k:sum(1 for w in ws if w in t) for k,ws in KEYWORDS.items()}
    best=max(scores,key=scores.get)
    return best if scores[best]>0 else "unknown"

def extract_candidate_atom(text, source_name="manual_source", registered_source_id=None):
    category=classify_text(text)
    sid=source_id(text)
    atom=create_dna_atom(
        name=f"candidate_{category}_{sid[:8]}",
        category=category,
        context=text[:240],
        trigger="TO_BE_VALIDATED_FROM_SOURCE",
        invalidation="TO_BE_VALIDATED_FROM_SOURCE",
        target="TO_BE_VALIDATED_FROM_SOURCE",
        risk="TO_BE_VALIDATED_FROM_SOURCE",
        success_conditions=["REQUIRES_BACKTEST","REQUIRES_OUT_OF_SAMPLE","REQUIRES_ROBUSTNESS"]
    )
    atom["source_name"]=source_name
    atom["source_id"]=sid
    atom["registered_source_id"]=registered_source_id
    atom["knowledge_status"]="CANDIDATE_NOT_VALIDATED"
    atom["edge_claim"]="NONE"
    return atom

def absorb_knowledge_texts(texts, source_name="manual_batch", registered_source_id=None, registry_path="mind_trader/reports/P8.88_knowledge_source_registry.json"):
    if not registered_source_id:
        return {"decision":"BLOCK_ABSORPTION_SOURCE_REQUIRED","production":"BLOCKED","edge_claim":"NONE"}
    src=require_source_registered(registered_source_id,registry_path)
    if not src["allowed"]:
        return {"decision":"BLOCK_ABSORPTION_SOURCE_NOT_REGISTERED","source_check":src,"production":"BLOCKED","edge_claim":"NONE"}

    atoms=[extract_candidate_atom(t,source_name,registered_source_id) for t in texts if str(t).strip()]
    report={
        "authority":"P8.89_KNOWLEDGE_ABSORPTION_WITH_SOURCE_REGISTRY",
        "created_at":datetime.now(UTC).isoformat(),
        "source_name":source_name,
        "registered_source_id":registered_source_id,
        "texts_seen":len(texts),
        "atoms_created":len(atoms),
        "atoms":atoms,
        "decision":"KNOWLEDGE_ABSORBED_AS_REGISTERED_CANDIDATES",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.89_knowledge_absorption_registered.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
