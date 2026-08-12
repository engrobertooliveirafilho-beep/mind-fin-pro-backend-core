import json
from pathlib import Path

data = json.loads(Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P4_73A_FULL_CAPABILITY_INVENTORY_20260618_200917\\capability_inventory.json").read_text(encoding="utf-8"))

print("SUMMARY:")
print(json.dumps(data["summary"], indent=2, ensure_ascii=False))

print("\nREADY_TO_INTEGRATE:")
for m in data["modules"]:
    if m["classification"] == "READY_TO_INTEGRATE":
        print("-", m["module"])
        print("  functions:", ", ".join(m["functions"][:20]))
        print("  classes:", ", ".join(m["classes"][:20]))

print("\nNEEDS_ADAPTER:")
for m in data["modules"]:
    if m["classification"] == "NEEDS_ADAPTER":
        print("-", m["module"])

print("\nP4.73A_FIX_READY_PRINT_COMPLETE")
