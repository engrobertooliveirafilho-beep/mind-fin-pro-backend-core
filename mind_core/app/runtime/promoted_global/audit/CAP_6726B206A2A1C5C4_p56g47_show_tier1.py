import json
from pathlib import Path

src=Path("reports/P5.6G46_EVIDENCE_PROMOTION_TRIAGE/P56G46_EVIDENCE_PROMOTION_TRIAGE.json")
data=json.loads(src.read_text(encoding="utf-8"))

tier1_progeny=[x for x in data["progeny"] if x["tier"]=="TIER_1_PROMOTABLE_REVIEW"]
tier1_valuation=[x for x in data["valuation"] if x["tier"]=="TIER_1_VALUATION_REVIEW"]

print("TIER1_PROGENY")
print(json.dumps(tier1_progeny,indent=2,ensure_ascii=False))

print("TIER1_VALUATION")
print(json.dumps(tier1_valuation,indent=2,ensure_ascii=False))
