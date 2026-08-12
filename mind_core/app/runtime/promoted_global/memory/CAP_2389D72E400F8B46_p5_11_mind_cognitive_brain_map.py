from __future__ import annotations
import ast, json, os, re, hashlib
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

REPO = Path(os.environ["P5_REPO"]).resolve()
OUT = Path(os.environ["P5_OUT"]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

CAPS = {
 "MEMORY":["memory","memoria","remember","recall","dialogue_memory","persistent"],
 "SEMANTIC_MEMORY":["semantic","embedding","vector","pgvector"],
 "SOCIAL_MEMORY":["social","relationship","profile","rapport"],
 "EMOTIONAL_MEMORY":["emotion","emotional","sentiment","mood"],
 "CONTEXT_RECOVERY":["context","recovery","continuity","dialogue_state"],
 "DECISION_MEMORY":["decision_memory","decision"],
 "RETRIEVAL":["retrieval","search","query","rank","index"],
 "KNOWLEDGE":["knowledge","kb","ontology","facts"],
 "REASONING":["reason","reasoning","infer","logic"],
 "REFLECTION":["reflection","reflexion","self_critique"],
 "PLANNING":["plan","planner","planning","goal"],
 "HIERARCHICAL_PLANNING":["hierarchy","hierarchical","decomposition","subgoal","task_tree"],
 "ORCHESTRATION":["orchestrator","orchestration","coordinate"],
 "ROUTING":["router","route","routing"],
 "DISPATCH":["dispatch","dispatcher"],
 "TOOL_USE":["tool","tools","tool_use"],
 "TOOL_SELECTION":["tool_selection","select_tool"],
 "AGENTS":["agent","agents"],
 "MULTI_AGENT":["multi_agent","multiagent","swarm"],
 "SIMULATION":["simulation","simulate","sandbox"],
 "LEARNING":["learning","learn","train","continuous_learning"],
 "GOVERNANCE":["governance","guardrail","compliance","authority"],
 "SAFETY":["safety","safe","moderation"],
 "HUMANIZATION":["humanization","humanize","natural_transition"],
 "PERSONALITY":["personality","persona","style"],
 "COMMUNICATION":["communication","conversation","response_builder"],
 "ACTION_CONTINUITY":["actionable","continuity","next_action"],
 "AUTONOMY":["autonomy","autonomous"],
 "COGNITIVE_CONTROL":["cognitive_control","control_loop","metacognition"]
}

CANON_HINTS = [
 "universal_conversation_os",
 "universal_conversation_authority",
 "actionable_continuity_authority",
 "p4_13g_router",
 "single_runtime_dispatcher",
 "semantic_memory_engine",
 "semantic_activation",
 "response_builder",
 "persistent_social_memory",
 "persistent_relationship_memory",
 "persistent_emotional_state",
 "humanization_runtime",
 "context_recovery",
 "decision_memory"
]

def now(): return datetime.now(timezone.utc).isoformat()

def read(p):
    try: return p.read_text(encoding="utf-8", errors="ignore")[:2_000_000]
    except Exception: return ""

def caps_for(name,path,text):
    blob=f"{name} {path} {text[:12000]}".lower()
    return sorted([cap for cap,kws in CAPS.items() if any(k.lower() in blob for k in kws)])

def extract_py(path,text):
    symbols=[]
    imports=[]
    calls=[]
    try: tree=ast.parse(text)
    except Exception: return symbols, imports, calls

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imports += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            imports.append(n.module or "")
        elif isinstance(n, ast.Call):
            try:
                calls.append(ast.unparse(n.func))
            except Exception:
                pass

    for n in ast.walk(tree):
        if isinstance(n,(ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            name=n.name
            typ="function"
            bases=[]
            decorators=[]
            if isinstance(n, ast.AsyncFunctionDef):
                typ="async_function"
            if isinstance(n, ast.ClassDef):
                typ="class"
                bases=[ast.unparse(b) for b in n.bases]
                decorators=[ast.unparse(d) for d in n.decorator_list]
                if any("BaseModel" in b for b in bases): typ="pydantic_model"
                if any("Enum" in b for b in bases): typ="enum"
                if any("dataclass" in d for d in decorators): typ="dataclass"
            symbols.append({
                "symbol_name":name,
                "type":typ,
                "file_path":str(path),
                "line":getattr(n,"lineno",None),
                "bases":bases,
                "decorators":decorators,
                "imports":sorted(set(imports)),
                "calls":sorted(set(calls))[:200],
                "capabilities":caps_for(name,str(path),text),
                "exported_api":not name.startswith("_"),
            })
    return symbols, imports, calls

def is_runtime_file(p):
    s=str(p).replace("\\","/").lower()
    if "/.venv/" in s or "/_evidence/" in s or "/.git/" in s or "__pycache__" in s:
        return False
    return s.endswith(".py")

all_symbols=[]
file_inventory=[]
edges=[]
for p in REPO.rglob("*.py"):
    if not is_runtime_file(p): continue
    txt=read(p)
    if not txt.strip(): continue
    syms, imports, calls = extract_py(p,txt)
    rel=str(p.relative_to(REPO)).replace("\\","/")
    file_caps=sorted(set(sum([s["capabilities"] for s in syms], [])))
    file_inventory.append({
        "file":rel,
        "size":p.stat().st_size,
        "capabilities":file_caps,
        "symbols":len(syms),
        "canonical_hint": any(h in rel.lower() or h in txt.lower() for h in CANON_HINTS)
    })
    for imp in imports:
        if imp.startswith("app."):
            edges.append({"from":rel,"to":imp,"type":"import"})
    all_symbols.extend(syms)

cap_to_symbols=defaultdict(list)
cap_to_files=defaultdict(set)
for s in all_symbols:
    for c in s["capabilities"]:
        cap_to_symbols[c].append(s)
        cap_to_files[c].add(s["file_path"])

status=[]
for cap in sorted(CAPS):
    count=len(cap_to_symbols.get(cap,[]))
    files=len(cap_to_files.get(cap,set()))
    active=sum(1 for f in cap_to_files.get(cap,set()) if "\\app\\runtime\\" in f.lower() or "/app/runtime/" in f.lower() or any(h in f.lower() for h in CANON_HINTS))
    if count == 0:
        exists="NÃO"; connected="NÃO"; maturity="TIER D"; review="MISSING"
    elif active > 0:
        exists="SIM"; connected="ATIVA"; maturity="TIER A" if count >= 5 else "TIER B"; review="OK"
    else:
        exists="PARCIAL"; connected="DESCONECTADA_OU_NAO_COMPROVADA"; maturity="TIER C"; review="REVISAR"
    status.append({
        "capability":cap,
        "exists":exists,
        "connectivity":connected,
        "symbol_count":count,
        "file_count":files,
        "active_evidence_count":active,
        "maturity":maturity,
        "review_status":review,
        "sample_symbols":cap_to_symbols.get(cap,[])[:15]
    })

dead=[]
unconnected=[]
for row in status:
    if row["exists"] != "NÃO" and row["connectivity"] != "ATIVA":
        unconnected.append(row)
    if row["exists"] == "PARCIAL" and row["active_evidence_count"] == 0:
        dead.append(row)

brain = {
    "mission":"P5.11_MIND_COGNITIVE_BRAIN_MAP",
    "created_at":now(),
    "repo_root":str(REPO),
    "build_allowed":False,
    "integration_allowed":False,
    "move_allowed":False,
    "archive_allowed":False,
    "code_changed":False,
    "files_scanned":len(file_inventory),
    "symbols_extracted":len(all_symbols),
    "capabilities_total":len(status),
    "capabilities_active":sum(1 for r in status if r["connectivity"]=="ATIVA"),
    "capabilities_missing":sum(1 for r in status if r["exists"]=="NÃO"),
    "capabilities_review":sum(1 for r in status if r["review_status"]=="REVISAR"),
    "brain_sections": {
        "MEMORY":[r for r in status if "MEMORY" in r["capability"]],
        "REASONING":[r for r in status if r["capability"] in ["REASONING","REFLECTION","COGNITIVE_CONTROL"]],
        "PLANNING":[r for r in status if "PLANNING" in r["capability"]],
        "EXECUTION":[r for r in status if r["capability"] in ["DISPATCH","ROUTING","ORCHESTRATION","ACTION_CONTINUITY"]],
        "AGENTS":[r for r in status if "AGENT" in r["capability"]],
        "TOOL_USE":[r for r in status if "TOOL" in r["capability"]],
        "HUMANIZATION":[r for r in status if r["capability"] in ["HUMANIZATION","PERSONALITY","SOCIAL_MEMORY","EMOTIONAL_MEMORY","COMMUNICATION"]],
        "GOVERNANCE":[r for r in status if r["capability"] in ["GOVERNANCE","SAFETY"]]
    }
}

gap_matrix=[r for r in status if r["exists"]=="NÃO" or r["review_status"]=="REVISAR"]

artifacts = {
    "MIND_BRAIN_MAP.json": brain,
    "MIND_COGNITIVE_GRAPH.json": {"nodes":status,"edges":edges},
    "MIND_RUNTIME_CONNECTIVITY_MATRIX.json": file_inventory,
    "MIND_CAPABILITY_STATUS_MATRIX.json": status,
    "MIND_GAP_MATRIX.json": gap_matrix,
    "MIND_DEAD_CAPABILITY_LEDGER.json": dead,
    "MIND_UNCONNECTED_CAPABILITY_LEDGER.json": unconnected,
    "MIND_SYMBOL_INDEX.json": all_symbols,
}

for name,data in artifacts.items():
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

md = f"""# P5.11 — MIND COGNITIVE BRAIN MAP

created_at: {now()}

## Summary

files_scanned: {len(file_inventory)}
symbols_extracted: {len(all_symbols)}
capabilities_total: {len(status)}
capabilities_active: {brain["capabilities_active"]}
capabilities_missing: {brain["capabilities_missing"]}
capabilities_review: {brain["capabilities_review"]}

## Locks

build_allowed: false
integration_allowed: false
move_allowed: false
archive_allowed: false
code_changed: false

## Missing / Review

{json.dumps(gap_matrix,ensure_ascii=False,indent=2)}
"""
(OUT/"MIND_BRAIN_MAP_REPORT.md").write_text(md,encoding="utf-8")

print(json.dumps({
 "STATUS":"P5_11_COMPLETE",
 "out_dir":str(OUT),
 "files_scanned":len(file_inventory),
 "symbols_extracted":len(all_symbols),
 "capabilities_active":brain["capabilities_active"],
 "capabilities_missing":brain["capabilities_missing"],
 "capabilities_review":brain["capabilities_review"],
 "code_changed":False
},ensure_ascii=False,indent=2))
