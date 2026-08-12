from __future__ import annotations

import ast
import json
import os
import re
import hashlib
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(os.environ.get("P5_REPO_ROOT", ".")).resolve()
DRIVE_ROOT = Path(os.environ.get("P5_DRIVE_ROOT", ".")).resolve()
OUT_DIR = Path(os.environ.get("P5_OUT_DIR", ".")).resolve()

BUILD_ALLOWED = False
INTEGRATION_ALLOWED = False
MOVE_ALLOWED = False
ARCHIVE_ALLOWED = False
CODE_CHANGED = False

TARGET_EXTS = {
    ".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml",
    ".csv", ".log", ".html", ".xml"
}

MAX_TEXT_BYTES = 2_000_000

CAPABILITY_KEYWORDS = {
    "MEMORY": ["memory", "memoria", "remember", "recall", "longterm", "shortterm"],
    "SEMANTIC_MEMORY": ["semantic", "embedding", "vector", "pgvector"],
    "VECTOR_MEMORY": ["vector", "embedding", "similarity"],
    "GRAPH_MEMORY": ["graph", "node", "edge", "knowledge_graph"],
    "SOCIAL_MEMORY": ["social", "relationship", "profile"],
    "EMOTIONAL_MEMORY": ["emotion", "emotional", "sentiment", "mood"],
    "CONTEXT_RECOVERY": ["context", "recovery", "dialogue_state", "continuity"],
    "RETRIEVAL": ["retrieval", "search", "rank", "index", "query"],
    "KNOWLEDGE": ["knowledge", "kb", "ontology", "facts"],
    "REASONING": ["reason", "reasoning", "infer", "logic"],
    "REFLECTION": ["reflection", "reflexion", "self_critique"],
    "META_REASONING": ["meta_reason", "metacognition", "cognitive_control"],
    "PLANNING": ["plan", "planner", "planning", "goal"],
    "HIERARCHICAL_PLANNING": ["hierarchy", "hierarchical", "tree", "decomposition"],
    "GOAL_DECOMPOSITION": ["goal_decomposition", "decompose", "subgoal"],
    "TASK_DECOMPOSITION": ["task", "subtask", "workbreakdown"],
    "EXECUTION": ["execute", "executor", "runner", "runtime"],
    "ORCHESTRATION": ["orchestrator", "orchestration", "coordinate"],
    "ROUTING": ["router", "route", "routing"],
    "DISPATCH": ["dispatch", "dispatcher"],
    "TOOL_USE": ["tool", "tools", "tooluse"],
    "TOOL_SELECTION": ["tool_selection", "select_tool"],
    "TOOL_PLANNING": ["tool_plan", "tool_routing"],
    "AGENTS": ["agent", "agents"],
    "MULTI_AGENT": ["multi_agent", "multiagent", "swarm"],
    "SIMULATION": ["simulation", "simulate", "sandbox"],
    "WORLD_MODEL": ["world_model", "environment"],
    "LEARNING": ["learning", "train", "learn"],
    "CONTINUOUS_LEARNING": ["continuous_learning", "online_learning"],
    "DECISION": ["decision", "decide", "policy"],
    "GOVERNANCE": ["governance", "guardrail", "compliance"],
    "SAFETY": ["safety", "safe", "moderation"],
    "PERSONALITY": ["personality", "persona", "style"],
    "SOCIAL_INTELLIGENCE": ["social_intelligence", "rapport", "empathy"],
    "HUMANIZATION": ["humanization", "humanize", "natural"],
    "COMMUNICATION": ["communication", "response", "conversation"],
    "ACTION_CONTINUITY": ["actionable", "continuity", "next_action"],
    "AUTONOMY": ["autonomy", "autonomous"],
    "LONG_TERM_MEMORY": ["long_term", "longterm"],
    "WORKING_MEMORY": ["working_memory", "scratchpad"],
    "COGNITIVE_CONTROL": ["cognitive_control", "control_loop"],
}

RUNTIME_COMPONENTS = {
    "Universal Conversation OS": ["universal_conversation_os", "conversation_os"],
    "Universal Conversation Authority": ["universal_conversation_authority", "ucca"],
    "Actionable Continuity Authority": ["actionable_continuity_authority", "aca"],
    "P4.13G Router": ["p4_13g_router", "router"],
    "Single Runtime Dispatcher": ["single_runtime_dispatcher", "dispatcher"],
    "Semantic Memory Engine": ["semantic_memory_engine", "semantic_memory"],
    "Semantic Activation": ["semantic_activation"],
    "Response Builder": ["response_builder"],
    "Persistent Social Memory": ["persistent_social_memory", "social_memory"],
    "Persistent Relationship Memory": ["relationship_memory"],
    "Persistent Emotional State": ["emotional_state", "emotional_memory"],
    "Humanization Runtime": ["humanization_runtime", "humanization"],
    "Context Recovery": ["context_recovery"],
    "Decision Memory": ["decision_memory"],
}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_read(path: Path) -> str:
    try:
        data = path.read_bytes()[:MAX_TEXT_BYTES]
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()

def classify_capabilities(name: str, path: str, text: str = "") -> list[str]:
    blob = f"{name} {path} {text[:5000]}".lower()
    caps = []
    for cap, kws in CAPABILITY_KEYWORDS.items():
        if any(k.lower() in blob for k in kws):
            caps.append(cap)
    return sorted(set(caps))

def extract_py_symbols(path: Path, text: str) -> list[dict[str, Any]]:
    out = []
    try:
        tree = ast.parse(text)
    except Exception:
        return out

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend([a.name for a in node.names])
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = []
            for d in getattr(node, "decorator_list", []):
                decorators.append(ast.unparse(d) if hasattr(ast, "unparse") else type(d).__name__)

            bases = []
            if isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b) if hasattr(ast, "unparse") else type(b).__name__ for b in node.bases]

            kind = "function"
            if isinstance(node, ast.AsyncFunctionDef):
                kind = "async_function"
            if isinstance(node, ast.ClassDef):
                kind = "class"
                if any("BaseModel" in b for b in bases):
                    kind = "pydantic_model"
                if any("Enum" in b for b in bases):
                    kind = "enum"
                if any("Protocol" in b for b in bases):
                    kind = "protocol"
                if any("TypedDict" in b for b in bases):
                    kind = "typeddict"
                if any("dataclass" in d for d in decorators):
                    kind = "dataclass"

            name = node.name
            caps = classify_capabilities(name, str(path), text)
            out.append({
                "symbol_name": name,
                "file_path": str(path),
                "module": str(path.relative_to(DRIVE_ROOT)) if str(path).startswith(str(DRIVE_ROOT)) else str(path),
                "type": kind,
                "line": getattr(node, "lineno", None),
                "decorators": decorators,
                "bases": bases,
                "imports": sorted(set(imports)),
                "dependencies": sorted(set(imports)),
                "references": [],
                "exported_api": name.startswith(("run", "execute", "plan", "build", "route", "dispatch", "search", "retrieve", "decide")) or not name.startswith("_"),
                "capabilities": caps,
            })
    return out

def extract_text_signals(path: Path, text: str) -> list[dict[str, Any]]:
    out = []
    patterns = [
        r"class\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"def\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"async\s+def\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"([A-Za-z_][A-Za-z0-9_]*(?:Engine|Agent|Planner|Orchestrator|Router|Dispatcher|Executor|Memory|Reasoner|Pipeline|Service|Controller|Model|Schema|DTO))",
    ]
    seen = set()
    for pat in patterns:
        for m in re.finditer(pat, text):
            name = m.group(1)
            if name in seen:
                continue
            seen.add(name)
            caps = classify_capabilities(name, str(path), text)
            if caps:
                out.append({
                    "symbol_name": name,
                    "file_path": str(path),
                    "module": str(path),
                    "type": "text_signal",
                    "line": None,
                    "imports": [],
                    "dependencies": [],
                    "references": [],
                    "exported_api": False,
                    "capabilities": caps,
                })
    return out

def iter_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TARGET_EXTS:
            yield p

def runtime_inventory(repo_root: Path) -> dict[str, Any]:
    found = defaultdict(list)
    runtime_files = []
    for p in repo_root.rglob("*.py"):
        rel = str(p.relative_to(repo_root)).replace("\\", "/").lower()
        if any(x in rel for x in ["app/runtime", "app/main", "app/cognition", "app/modules", "app/mind"]):
            txt = safe_read(p)
            runtime_files.append(str(p))
            blob = f"{rel}\n{txt}".lower()
            for comp, kws in RUNTIME_COMPONENTS.items():
                if any(k.lower() in blob for k in kws):
                    found[comp].append(str(p))
    return {
        "runtime_root": str(repo_root),
        "runtime_files_scanned": len(runtime_files),
        "components_found": {k: sorted(set(v)) for k, v in found.items()},
    }

def coverage_status(cap: str, runtime: dict[str, Any]) -> str:
    blob = json.dumps(runtime, ensure_ascii=False).lower()
    keywords = CAPABILITY_KEYWORDS.get(cap, [])
    hits = sum(1 for k in keywords if k.lower() in blob)
    if hits >= 2:
        return "PRESENT"
    if hits == 1:
        return "PARTIAL"
    return "MISSING"

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    symbols = []
    file_count = 0
    readable_count = 0
    skipped_count = 0

    for p in iter_files(DRIVE_ROOT):
        file_count += 1
        txt = safe_read(p)
        if not txt.strip():
            skipped_count += 1
            continue
        readable_count += 1

        if p.suffix.lower() == ".py":
            extracted = extract_py_symbols(p, txt)
        else:
            extracted = extract_text_signals(p, txt)

        for item in extracted:
            item["file_sha1"] = sha1_text(txt)
            symbols.append(item)

        if file_count % 10000 == 0:
            print(f"[scan] files={file_count} readable={readable_count} symbols={len(symbols)}")

    cap_to_symbols = defaultdict(list)
    for s in symbols:
        for cap in s.get("capabilities", []):
            cap_to_symbols[cap].append(s)

    runtime = runtime_inventory(REPO_ROOT)

    coverage = []
    for cap, items in sorted(cap_to_symbols.items()):
        status = coverage_status(cap, runtime)
        coverage.append({
            "capability": cap,
            "status": status,
            "symbol_count": len(items),
            "sample_symbols": items[:20],
        })

    gaps = []
    for row in coverage:
        if row["status"] in {"MISSING", "PARTIAL"}:
            priority = "LOW_VALUE_GAP"
            if row["capability"] in {"HIERARCHICAL_PLANNING", "GOAL_DECOMPOSITION", "PLANNING", "ORCHESTRATION", "TOOL_PLANNING"}:
                priority = "HIGH_VALUE_GAP"
            elif row["capability"] in {"REASONING", "REFLECTION", "MULTI_AGENT", "COGNITIVE_CONTROL"}:
                priority = "MEDIUM_VALUE_GAP"
            gaps.append({**row, "gap_priority": priority})

    dup_counter = Counter((s["symbol_name"], tuple(s.get("capabilities", []))) for s in symbols)
    duplication = []
    for key, count in dup_counter.items():
        if count > 1:
            name, caps = key
            duplication.append({
                "symbol_name": name,
                "capabilities": list(caps),
                "count": count,
                "classification": "DUPLICATE" if count < 20 else "LEGACY_OR_GENERATED_DUPLICATE",
            })

    ranking = []
    for row in coverage:
        cap = row["capability"]
        score = row["symbol_count"]
        tier = "TIER D"
        if cap in {"HIERARCHICAL_PLANNING", "GOAL_DECOMPOSITION", "PLANNING", "ORCHESTRATION"}:
            tier = "TIER S"
        elif cap in {"REASONING", "REFLECTION", "CONTEXT_RECOVERY", "MEMORY", "SEMANTIC_MEMORY", "MULTI_AGENT"}:
            tier = "TIER A"
        elif score > 100:
            tier = "TIER B"
        elif score > 10:
            tier = "TIER C"
        ranking.append({**row, "tier": tier})

    final = {
        "mission": "P5.10_DRIVE_EXHAUSTIVE_CAPABILITY_CERTIFICATION",
        "created_at": utc_now(),
        "build_allowed": BUILD_ALLOWED,
        "integration_allowed": INTEGRATION_ALLOWED,
        "move_allowed": MOVE_ALLOWED,
        "archive_allowed": ARCHIVE_ALLOWED,
        "code_changed": CODE_CHANGED,
        "drive_root": str(DRIVE_ROOT),
        "repo_root": str(REPO_ROOT),
        "files_scanned": file_count,
        "readable_scanned": readable_count,
        "symbols_extracted": len(symbols),
        "capabilities_detected": len(cap_to_symbols),
        "runtime_components_found": runtime["components_found"],
        "real_missing_capabilities": [g for g in gaps if g["gap_priority"] in {"HIGH_VALUE_GAP", "CRITICAL_GAP"}],
        "all_gaps": gaps,
        "audit_complete": True,
        "drive_capabilities_remaining": 0 if not gaps else len(gaps),
        "final_answer": "NAO" if gaps else "SIM",
        "can_close_drive_audit": False if gaps else True,
    }

    artifacts = {
        "GLOBAL_SYMBOL_INDEX.json": symbols,
        "CAPABILITY_NORMALIZATION_GRAPH.json": {
            "normalization_rules": CAPABILITY_KEYWORDS,
            "capability_to_symbol_count": {k: len(v) for k, v in cap_to_symbols.items()},
        },
        "GLOBAL_CAPABILITY_GRAPH.json": {
            "nodes": list(cap_to_symbols.keys()),
            "edges": [
                {"capability": cap, "symbol": s["symbol_name"], "file": s["file_path"]}
                for cap, arr in cap_to_symbols.items()
                for s in arr[:500]
            ],
        },
        "CAPABILITY_CLUSTER_MATRIX.json": coverage,
        "DUPLICATION_LEDGER.json": duplication,
        "RUNTIME_COVERAGE_MATRIX.json": {
            "runtime": runtime,
            "coverage": coverage,
        },
        "EXHAUSTIVE_GAP_LEDGER.json": gaps,
        "DEEP_GAP_INVESTIGATION_REPORT.json": {
            "deep_gap_count": len(gaps),
            "gaps": gaps,
        },
        "CAPABILITY_PRIORITY_RANKING.json": ranking,
        "FINAL_GAP_CERTIFICATION.json": final,
    }

    for name, data in artifacts.items():
        (OUT_DIR / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    md = f"""# FINAL EXECUTIVE VERDICT — P5.10

created_at: {utc_now()}

## BLOQUEIOS

build_allowed = false  
integration_allowed = false  
move_allowed = false  
archive_allowed = false  
code_changed = false  

## RESULTADO

files_scanned = {file_count}  
readable_scanned = {readable_count}  
symbols_extracted = {len(symbols)}  
capabilities_detected = {len(cap_to_symbols)}  
gaps_detected = {len(gaps)}  

## RESPOSTA CENTRAL

A Eldora já possui todas as capabilities cognitivas relevantes encontradas no Drive?

{final["final_answer"]}

## Auditoria do Drive pode ser encerrada?

{"SIM" if final["can_close_drive_audit"] else "NÃO"}

## High-value gaps

{json.dumps(final["real_missing_capabilities"], ensure_ascii=False, indent=2)}
"""
    (OUT_DIR / "FINAL_EXECUTIVE_VERDICT.md").write_text(md, encoding="utf-8")

    print(json.dumps({
        "STATUS": "P5_10_COMPLETE",
        "out_dir": str(OUT_DIR),
        "files_scanned": file_count,
        "readable_scanned": readable_count,
        "symbols_extracted": len(symbols),
        "capabilities_detected": len(cap_to_symbols),
        "gaps_detected": len(gaps),
        "code_changed": False,
        "build_allowed": False,
        "integration_allowed": False,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
