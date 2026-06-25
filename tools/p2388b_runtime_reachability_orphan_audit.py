import ast, csv, json, os, re
from pathlib import Path
from collections import defaultdict, deque

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

SKIP_DIRS={
    ".git","__pycache__",".pytest_cache",".venv","venv","env",
    "node_modules","_evidence","htmlcov",".mypy_cache"
}

ROOT_HINTS=[
    "main.py",
    "app/main.py",
    "app/api",
    "app/runtime",
    "tools",
]

CRITICAL_KEYWORDS=[
    "trader","de40","paper","mt5","ftmo","signal","bridge",
    "playbook","xray","regime","context","lifecycle","footprint",
    "forward","monitor","governance","risk","order"
]

DANGEROUS_PATTERNS=[
    "ORDER_TYPE_BUY",
    "ORDER_TYPE_SELL",
    "order_send",
    "mt5.order_send",
    "TRADE_ACTION_DEAL",
    "REAL_ORDERS=True",
    "FTMO_REAL=True",
    "LIVE_ORDER",
    "REAL_ORDER",
]

def safety():
    assert MODE=="PAPER_ONLY"
    assert REAL_ORDERS=="FORBIDDEN"
    assert FTMO_REAL=="FORBIDDEN"

def write_csv(path, rows, fields):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

def rel(root, path):
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve())).replace("\\","/")
    except Exception:
        return str(path).replace("\\","/")

def module_name(root, path):
    r=rel(root,path)
    if not r.endswith(".py"):
        return ""
    r=r[:-3]
    parts=[p for p in r.split("/") if p != "__init__"]
    return ".".join(parts)

def scan_files(root):
    files=[]
    for p in Path(root).rglob("*.py"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        files.append(p)
    return sorted(files)

def parse_imports(path):
    imports=[]
    try:
        tree=ast.parse(path.read_text(encoding="utf-8",errors="ignore"))
    except Exception:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports

def parse_defs(path):
    funcs=[]
    classes=[]
    try:
        tree=ast.parse(path.read_text(encoding="utf-8",errors="ignore"))
    except Exception:
        return funcs,classes

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            funcs.append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            funcs.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
    return funcs,classes

def imported_internal(import_name, module_map):
    hits=[]
    for mod in module_map:
        if import_name == mod or import_name.startswith(mod+".") or mod.startswith(import_name+"."):
            hits.append(mod)
    return hits

def classify_file(path, text):
    low=str(path).lower()+" "+text.lower()
    tags=[]
    for k in CRITICAL_KEYWORDS:
        if k in low:
            tags.append(k.upper())
    return "|".join(sorted(set(tags))) if tags else "GENERAL"

def run(root,evidence_root,outdir):
    safety()
    root=Path(root)
    out=Path(outdir)
    out.mkdir(parents=True,exist_ok=True)

    py_files=scan_files(root)
    module_map={module_name(root,p):p for p in py_files}

    file_rows=[]
    import_edges=[]
    defs_rows=[]
    dangerous_rows=[]
    reference_count=defaultdict(int)
    reverse_refs=defaultdict(list)

    all_text_cache={}

    for p in py_files:
        text=p.read_text(encoding="utf-8",errors="ignore")
        all_text_cache[p]=text
        mod=module_name(root,p)
        imports=parse_imports(p)
        funcs,classes=parse_defs(p)
        tags=classify_file(p,text)

        for imp in imports:
            hits=imported_internal(imp,module_map)
            for h in hits:
                import_edges.append({
                    "from_module":mod,
                    "to_module":h,
                    "import_name":imp,
                    "from_file":rel(root,p),
                    "to_file":rel(root,module_map[h])
                })
                reference_count[h]+=1
                reverse_refs[h].append(mod)

        for fn in funcs:
            defs_rows.append({"module":mod,"file":rel(root,p),"type":"function","name":fn})
        for cl in classes:
            defs_rows.append({"module":mod,"file":rel(root,p),"type":"class","name":cl})

        for pat in DANGEROUS_PATTERNS:
            if pat in text:
                dangerous_rows.append({
                    "file":rel(root,p),
                    "module":mod,
                    "pattern":pat,
                    "severity":"HIGH" if "order_send" in pat.lower() or "TRADE_ACTION_DEAL" in pat else "MEDIUM"
                })

        file_rows.append({
            "module":mod,
            "file":rel(root,p),
            "size":p.stat().st_size,
            "imports":len(imports),
            "functions":len(funcs),
            "classes":len(classes),
            "tags":tags,
            "is_trader_related":any(k in tags for k in ["TRADER","DE40","PAPER","MT5","FTMO","SIGNAL","BRIDGE","PLAYBOOK"]),
        })

    # Textual reference scan: catches dynamic imports / string references.
    textual_refs=[]
    module_names=list(module_map.keys())
    for mod,p in module_map.items():
        text=all_text_cache[p]
        for target in module_names:
            if target==mod:
                continue
            base=target.split(".")[-1]
            if base and re.search(r"\b"+re.escape(base)+r"\b", text):
                textual_refs.append({
                    "from_module":mod,
                    "to_module_candidate":target,
                    "from_file":rel(root,p),
                    "to_file":rel(root,module_map[target]),
                    "reference_type":"TEXTUAL_SYMBOL"
                })
                reference_count[target]+=1

    # Entry points
    entry_modules=set()
    for hint in ROOT_HINTS:
        hp=root/hint
        if hp.is_file() and hp.suffix==".py":
            entry_modules.add(module_name(root,hp))
        elif hp.is_dir():
            for p in hp.rglob("*.py"):
                if any(part in SKIP_DIRS for part in p.parts):
                    continue
                entry_modules.add(module_name(root,p))

    graph=defaultdict(set)
    for e in import_edges:
        graph[e["from_module"]].add(e["to_module"])

    reachable=set()
    q=deque(entry_modules)
    while q:
        m=q.popleft()
        if m in reachable:
            continue
        reachable.add(m)
        for nxt in graph.get(m,[]):
            if nxt not in reachable:
                q.append(nxt)

    orphan_rows=[]
    reachable_rows=[]
    for mod,p in module_map.items():
        tags=next((r["tags"] for r in file_rows if r["module"]==mod),"")
        is_critical=any(k in tags for k in ["TRADER","DE40","PAPER","MT5","FTMO","SIGNAL","BRIDGE","PLAYBOOK","REGIME","CONTEXT"])
        row={
            "module":mod,
            "file":rel(root,p),
            "reachable":mod in reachable,
            "direct_import_refs":len(reverse_refs.get(mod,[])),
            "total_refs":reference_count.get(mod,0),
            "tags":tags,
            "is_critical":is_critical
        }
        reachable_rows.append(row)
        if mod not in reachable and reference_count.get(mod,0)==0 and is_critical:
            orphan_rows.append(row)

    evidence_dirs=[p for p in Path(evidence_root).glob("P*") if p.is_dir()]
    evidence_rows=[]
    for d in evidence_dirs:
        summary=d/"summary.json"
        obj=None
        if summary.exists():
            try:
                obj=json.loads(summary.read_text(encoding="utf-8"))
            except Exception:
                obj=None
        evidence_rows.append({
            "evidence_dir":str(d),
            "name":d.name,
            "has_summary":summary.exists(),
            "mode":obj.get("mode","") if obj else "",
            "real_orders":obj.get("real_orders","") if obj else "",
            "ftmo_real":obj.get("ftmo_real","") if obj else "",
            "certification":obj.get("certification","") if obj else "",
            "next_required":obj.get("next_required","") if obj else "",
        })

    broken_evidence=[
        r for r in evidence_rows
        if (r["mode"] and r["mode"]!="PAPER_ONLY")
        or (r["real_orders"] and r["real_orders"]!="FORBIDDEN")
        or (r["ftmo_real"] and r["ftmo_real"]!="FORBIDDEN")
    ]

    write_csv(out/"runtime_files.csv",file_rows,list(file_rows[0].keys()) if file_rows else ["module"])
    write_csv(out/"runtime_import_edges.csv",import_edges,list(import_edges[0].keys()) if import_edges else ["from_module"])
    write_csv(out/"runtime_textual_refs.csv",textual_refs,list(textual_refs[0].keys()) if textual_refs else ["from_module"])
    write_csv(out/"runtime_defs.csv",defs_rows,list(defs_rows[0].keys()) if defs_rows else ["module"])
    write_csv(out/"runtime_reachability.csv",reachable_rows,list(reachable_rows[0].keys()) if reachable_rows else ["module"])
    write_csv(out/"runtime_orphans_critical.csv",orphan_rows,list(orphan_rows[0].keys()) if orphan_rows else ["module"])
    write_csv(out/"runtime_dangerous_patterns.csv",dangerous_rows,list(dangerous_rows[0].keys()) if dangerous_rows else ["file"])
    write_csv(out/"evidence_summary_audit.csv",evidence_rows,list(evidence_rows[0].keys()) if evidence_rows else ["evidence_dir"])
    write_csv(out/"evidence_broken_safety.csv",broken_evidence,list(broken_evidence[0].keys()) if broken_evidence else ["evidence_dir"])

    dot="digraph RUNTIME_REACHABILITY {\nrankdir=LR;\n"
    for r in reachable_rows:
        color="green" if r["reachable"] else ("red" if r["is_critical"] else "gray")
        label=(r["module"]+"\\n"+r["tags"]).replace('"','')
        dot += f'"{r["module"]}" [label="{label}", color={color}];\n'
    for e in import_edges:
        dot += f'"{e["from_module"]}" -> "{e["to_module"]}";\n'
    dot += "}\n"
    (out/"runtime_reachability.dot").write_text(dot,encoding="utf-8")

    critical_files=[r for r in file_rows if r["is_trader_related"]]
    critical_unreachable=[r for r in reachable_rows if r["is_critical"] and not r["reachable"]]
    high_danger=[r for r in dangerous_rows if r["severity"]=="HIGH"]

    certified=(
        len(broken_evidence)==0
        and len(high_danger)==0
        and len(orphan_rows)==0
    )

    summary={
        "mission":"P2388B_TRADER_RUNTIME_REACHABILITY_ORPHAN_AUDIT",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "root":str(root),
        "evidence_root":str(evidence_root),
        "output":str(out),
        "python_files":len(py_files),
        "modules":len(module_map),
        "import_edges":len(import_edges),
        "textual_refs":len(textual_refs),
        "definitions":len(defs_rows),
        "entry_modules":len(entry_modules),
        "reachable_modules":len(reachable),
        "critical_files":len(critical_files),
        "critical_unreachable":len(critical_unreachable),
        "critical_orphans":len(orphan_rows),
        "dangerous_patterns":len(dangerous_rows),
        "high_dangerous_patterns":len(high_danger),
        "evidence_dirs":len(evidence_rows),
        "broken_evidence_safety":len(broken_evidence),
        "certification":"P2388B_RUNTIME_REACHABILITY_CERTIFIED" if certified else "P2388B_RUNTIME_REACHABILITY_REQUIRES_REPAIR",
        "next_required":"P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK" if certified else "P2388C_RUNTIME_ORPHAN_REPAIR"
    }

    with open(out/"summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)

    return summary

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--evidence-root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.root,a.evidence_root,a.out),indent=2,ensure_ascii=False))
