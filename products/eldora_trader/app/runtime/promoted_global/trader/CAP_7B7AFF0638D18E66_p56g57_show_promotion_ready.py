import json
from pathlib import Path

p=Path("reports/P5.6G56_PROMOTION_POLICY_FOR_PROVISIONAL_EDGES/P56G56_PROMOTION_POLICY_AUDIT.json")
data=json.loads(p.read_text(encoding="utf-8"))

ready=[e for e in data["edges"] if e["promotion_tier"]=="PROMOTION_READY_REVIEW"]

print(json.dumps(ready,indent=2,ensure_ascii=False))
