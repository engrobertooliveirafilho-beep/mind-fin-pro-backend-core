from __future__ import annotations

import ast
import inspect
import importlib
import json
from pathlib import Path
from datetime import datetime, timezone

EVID = Path("_evidence/P19P36J_RECOVERED_MEMORY_CONTRACT_AUDIT_20260621_230647")

MODULES = [
    "app.runtime.memory_adapter",
    "app.runtime.memory_store",
    "app.runtime.followup_unified_resolver",
    "app.runtime.generic_topic_memory_engine",
    "app.vision.vision_memory_store",
]

def source_path(module_name: str):
    return Path(module_name.replace(".", "/") + ".py")

def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def ast_contract(path: Path):
    txt = safe_read(path)
    result = {
        "functions": [],
        "classes": [],
        "assignments": [],
        "path_refs": [],
        "json_refs": [],
        "store_refs": [],
    }

    try:
        tree = ast.parse(txt)
    except Exception as e:
        result["parse_error"] = repr(e)
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "args": [a.arg for a in node.args.args],
                "returns": ast.unparse(node.returns) if node.returns else ""
            })
        elif isinstance(node, ast.ClassDef):
            methods = []
            for n in node.body:
                if isinstance(n, ast.FunctionDef):
                    methods.append({
                        "name": n.name,
                        "line": n.lineno,
                        "args": [a.arg for a in n.args.args]
                    })
            result["classes"].append({
                "name": node.name,
                "line": node.lineno,
                "methods": methods
            })
        elif isinstance(node, ast.Assign):
            try:
                target = ast.unparse(node.targets[0])
                value = ast.unparse(node.value)
                result["assignments"].append({"target": target, "value": value[:300]})
            except Exception:
                pass

    low = txt.lower()
    for line in txt.splitlines():
        l = line.strip()
        ll = l.lower()
        if "path(" in ll or "_runtime" in ll or ".json" in ll or ".jsonl" in ll:
            result["path_refs"].append(l[:300])
        if "json" in ll:
            result["json_refs"].append(l[:300])
        if "store" in ll or "memory" in ll or "recall" in ll or "save" in ll:
            result["store_refs"].append(l[:300])

    return result

def runtime_contract(module_name: str):
    item = {
        "module": module_name,
        "import_ok": False,
        "members": [],
        "experiments": []
    }

    try:
        mod = importlib.import_module(module_name)
        item["import_ok"] = True

        for name, obj in inspect.getmembers(mod):
            if name.startswith("_"):
                continue
            if inspect.isfunction(obj) or inspect.isclass(obj):
                try:
                    sig = str(inspect.signature(obj))
                except Exception:
                    sig = ""
                item["members"].append({
                    "name": name,
                    "kind": "class" if inspect.isclass(obj) else "function",
                    "signature": sig,
                    "doc": (inspect.getdoc(obj) or "")[:300]
                })

        experiments = [
            ("safe_recall", [("+TEST",), ("+TEST", "quero emagrecer")]),
            ("safe_recall_with_fallback", [("+TEST",), ("+TEST", "quero emagrecer")]),
            ("is_followup", [("quais",), ("continue",), ("e depois",)]),
            ("resolve_followup", [("+TEST", "quais"), ("+TEST", "continue")]),
            ("extract_subject", [("quero abrir escola de inglês",), ("quero emagrecer",)]),
            ("infer_domain", [("quero emagrecer",), ("quero validar FTMO",), ("como montar escola",)]),
            ("expand_followup", [("quais", {"active_subject": "quero emagrecer"}), ("continue", {"active_subject": "abrir franquia"})]),
            ("update_topic_context", [("quero emagrecer", {}, "fitness"), ("quero abrir escola", {}, "")]),
        ]

        for fn_name, arg_sets in experiments:
            fn = getattr(mod, fn_name, None)
            if not callable(fn):
                continue
            for args in arg_sets:
                try:
                    val = fn(*args)
                    item["experiments"].append({
                        "function": fn_name,
                        "args": str(args),
                        "ok": True,
                        "result_type": type(val).__name__,
                        "result_preview": str(val)[:700]
                    })
                except Exception as e:
                    item["experiments"].append({
                        "function": fn_name,
                        "args": str(args),
                        "ok": False,
                        "error": repr(e)
                    })

        # class experiments
        for class_name in ["SimpleMemoryStore", "VisionMemoryStore"]:
            cls = getattr(mod, class_name, None)
            if cls and inspect.isclass(cls):
                try:
                    inst = cls()
                    methods = []
                    for n, o in inspect.getmembers(inst):
                        if not n.startswith("_") and callable(o):
                            try:
                                sig = str(inspect.signature(o))
                            except Exception:
                                sig = ""
                            methods.append({"name": n, "signature": sig})
                    item["experiments"].append({
                        "class": class_name,
                        "ok": True,
                        "methods": methods
                    })

                    for method_name in ["get", "save", "load", "recall", "remember", "set", "append", "add", "search"]:
                        method = getattr(inst, method_name, None)
                        if callable(method):
                            for args in [("+TEST",), ("+TEST", "quero emagrecer"), ("+TEST", {"x": 1})]:
                                try:
                                    val = method(*args)
                                    item["experiments"].append({
                                        "class": class_name,
                                        "method": method_name,
                                        "args": str(args),
                                        "ok": True,
                                        "result_type": type(val).__name__,
                                        "result_preview": str(val)[:700]
                                    })
                                except Exception as e:
                                    item["experiments"].append({
                                        "class": class_name,
                                        "method": method_name,
                                        "args": str(args),
                                        "ok": False,
                                        "error": repr(e)
                                    })
                except Exception as e:
                    item["experiments"].append({
                        "class": class_name,
                        "ok": False,
                        "error": repr(e)
                    })

    except Exception as e:
        item["error"] = repr(e)

    return item

contracts = []
for m in MODULES:
    path = source_path(m)
    contracts.append({
        "module": m,
        "path": path.as_posix(),
        "source_exists": path.exists(),
        "ast_contract": ast_contract(path),
        "runtime_contract": runtime_contract(m),
    })

EVID.mkdir(parents=True, exist_ok=True)
(EVID / "recovered_memory_contracts.json").write_text(
    json.dumps({
        "mission": "P19P36J_RECOVERED_MEMORY_CONTRACT_AUDIT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "contracts": contracts
    }, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

for c in contracts:
    print("\n===", c["module"], "===")
    print("source_exists:", c["source_exists"])
    print("functions:", [f["name"] for f in c["ast_contract"].get("functions", [])])
    print("classes:", [cl["name"] for cl in c["ast_contract"].get("classes", [])])
    print("runtime members:", [(m["kind"], m["name"], m["signature"]) for m in c["runtime_contract"].get("members", [])])
    print("experiments:")
    for e in c["runtime_contract"].get("experiments", [])[:30]:
        print(" ", e)
