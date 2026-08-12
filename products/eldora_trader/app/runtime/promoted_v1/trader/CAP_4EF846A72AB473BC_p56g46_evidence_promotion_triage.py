import json, re
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G46_EVIDENCE_PROMOTION_TRIAGE"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

def load_json_safe(path):
    p=Path(path)
    for enc in ["utf-8","utf-8-sig","cp1252","latin1"]:
        try:
            return json.loads(p.read_text(encoding=enc, errors="replace"))
        except Exception:
            pass
    raise RuntimeError(f"Unable to decode {path}")

progeny=load_json_safe("reports/P5.6G45_SIGNAL_TRIAGE/P56G45_PROGENY_LEDGER.json")
valuation=load_json_safe("reports/P5.6G45_SIGNAL_TRIAGE/P56G45_VALUATION_LEDGER.json")

def tier(record, kind):
    text=" ".join(str(record.get(x,"")) for x in ["title","source_url","signal_terms"]).lower()
    score=float(record.get("score",0) or 0)

    if any(x in text for x in ["etsy.com","fan page","facebook.com/bushwackerpbrbuckingbull"]):
        return "TIER_4_NOISE"

    if kind=="progeny":
        if re.search(r"(son|daughter|offspring|progeny)\s+of\s+", text) or score>=200:
            return "TIER_1_PROMOTABLE_REVIEW"
        if score>=150:
            return "TIER_2_RESEARCH"
        return "TIER_3_WEAK"

    if kind=="valuation":
        if any(x in text for x in ["semen","embryo","lot"]) and score>=180:
            return "TIER_1_VALUATION_REVIEW"
        if any(x in text for x in ["sold","auction","sale","$"]) and score>=160:
            return "TIER_2_VALUATION_RESEARCH"
        return "TIER_3_WEAK"

triaged={
 "mission":MISSION,
 "mode":"TRIAGE_ONLY_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "progeny":[],
 "valuation":[],
 "summary":{},
 "status":"PASS"
}

for r in progeny:
    r["tier"]=tier(r,"progeny")
    triaged["progeny"].append(r)

for r in valuation:
    r["tier"]=tier(r,"valuation")
    triaged["valuation"].append(r)

summary={}
for bucket in ["progeny","valuation"]:
    counts={}
    for r in triaged[bucket]:
        counts[r["tier"]]=counts.get(r["tier"],0)+1
    summary[bucket]=counts

triaged["summary"]=summary

(out/"P56G46_EVIDENCE_PROMOTION_TRIAGE.json").write_text(
 json.dumps(triaged,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(summary,indent=2,ensure_ascii=False))
print("OUTPUT =",out)
