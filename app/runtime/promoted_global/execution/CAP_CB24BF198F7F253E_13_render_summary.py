import json
from pathlib import Path

e = Path(r"_evidence\\P19P36B_RUNTIME_DEPENDENCY_GRAPH_20260621_222624")
summary = json.loads((e / "runtime_dependency_summary.json").read_text(encoding="utf-8"))
dead = json.loads((e / "runtime_dead_modules.json").read_text(encoding="utf-8"))
dups = json.loads((e / "runtime_duplicate_modules.json").read_text(encoding="utf-8"))
entries = json.loads((e / "runtime_entrypoints.json").read_text(encoding="utf-8"))

print("=== SUMMARY ===")
print(json.dumps(summary, ensure_ascii=False, indent=2))

print("\n=== ENTRYPOINTS ===")
for x in entries["entrypoints"][:80]:
    print(x)

print("\n=== DEAD CANDIDATES TOP 80 ===")
for x in dead[:80]:
    print(x["path"], "=>", ",".join(x["capabilities"]))

print("\n=== DUPLICATE GROUPS ===")
for g in dups[:40]:
    print(g["capability_group"], "COUNT", g["count"])
    for p in g["paths"][:20]:
        print("  -", p)
