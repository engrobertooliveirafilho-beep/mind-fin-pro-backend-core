import json
from pathlib import Path

LEDGER = Path("runtime/capability_usage_ledger.jsonl")

summary = {}

if LEDGER.exists():
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except:
            continue

        cap = row["capability"]

        if cap not in summary:
            summary[cap] = {
                "total":0,
                "success":0,
                "failed":0
            }

        summary[cap]["total"] += 1

        if row["success"]:
            summary[cap]["success"] += 1
        else:
            summary[cap]["failed"] += 1

print(json.dumps(summary,indent=2,ensure_ascii=False))
