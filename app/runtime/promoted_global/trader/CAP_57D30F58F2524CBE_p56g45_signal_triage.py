import json,re
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G45_SIGNAL_TRIAGE"

src=Path(
"reports/P5.6G44_PROGENY_AND_VALUATION_EXPANSION/P56G44_PROGENY_VALUATION_EXPANSION_LEDGER.json"
)

data=json.loads(src.read_text(encoding="utf-8"))

out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

PROGENY_TERMS={
 "offspring":50,
 "progeny":50,
 "daughter":45,
 "son":45,
 "calf":35,
 "calves":35
}

VALUE_TERMS={
 "auction":50,
 "sold":45,
 "sale":40,
 "embryo":40,
 "semen":40,
 "breeding rights":50,
 "catalog":25,
 "lot":20,
 "$":15
}

progeny=[]
valuation=[]
rejected=[]

for s in data["signals"]:

    score=0

    for t in s["signal_terms"]:
        score += PROGENY_TERMS.get(t,0)
        score += VALUE_TERMS.get(t,0)

    try:
        score += float(s["confidence_score"])
    except:
        pass

    record={
        "target":s["target"],
        "source_id":s["source_id"],
        "score":round(score,2),
        "signal_terms":s["signal_terms"],
        "title":s["title"],
        "source_url":s["source_url"]
    }

    prog=max([PROGENY_TERMS.get(x,0) for x in s["signal_terms"]] or [0])
    val=max([VALUE_TERMS.get(x,0) for x in s["signal_terms"]] or [0])

    if prog >= val and prog>0:
        progeny.append(record)
    elif val>0:
        valuation.append(record)
    else:
        rejected.append(record)

progeny.sort(key=lambda x:x["score"],reverse=True)
valuation.sort(key=lambda x:x["score"],reverse=True)

summary={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "progeny_candidates":len(progeny),
 "valuation_candidates":len(valuation),
 "rejected":len(rejected),
 "top_progeny":progeny[:25],
 "top_valuation":valuation[:25]
}

(out/"P56G45_PROGENY_LEDGER.json").write_text(
 json.dumps(progeny,indent=2,ensure_ascii=False)
)

(out/"P56G45_VALUATION_LEDGER.json").write_text(
 json.dumps(valuation,indent=2,ensure_ascii=False)
)

(out/"P56G45_REJECTED_LEDGER.json").write_text(
 json.dumps(rejected,indent=2,ensure_ascii=False)
)

(out/"P56G45_SUMMARY.json").write_text(
 json.dumps(summary,indent=2,ensure_ascii=False)
)

print(json.dumps({
 "progeny_candidates":len(progeny),
 "valuation_candidates":len(valuation),
 "rejected":len(rejected)
},indent=2))

print("OUTPUT =",out)
