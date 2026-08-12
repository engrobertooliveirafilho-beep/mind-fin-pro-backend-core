import os, re, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G44_PROGENY_AND_VALUATION_EXPANSION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

targets=[
 "Bushwacker","REINDEER","MO 110","DIAMOND'S GHOST",
 "NACCARATO BREEDING","JR 34","ORIGINAL JR","JR 3"
]

keywords=[
 "son","daughter","offspring","progeny","calf","calves",
 "semen","embryo","sale","auction","sold","breeding rights",
 "$","lot","catalog"
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

result={
 "mission":MISSION,
 "mode":"EVIDENCE_DISCOVERY_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "targets":targets,
 "signals":[],
 "summary":{},
 "status":"UNKNOWN"
}

for t in targets:
    cur.execute("""
    select id, source_url, source_type, title, confidence_score, validation_status, raw_payload
    from p55a_sources
    where lower(coalesce(title,'')) like lower(%s)
       or lower(coalesce(raw_payload::text,'')) like lower(%s)
       or lower(coalesce(source_url,'')) like lower(%s)
    order by confidence_score desc nulls last
    limit 200
    """,(f"%{t}%",f"%{t}%",f"%{t}%"))

    rows=cur.fetchall()

    for r in rows:
        text=(str(r[3] or "")+" "+str(r[6] or "")+" "+str(r[1] or "")).lower()
        hits=[k for k in keywords if k in text]
        if hits:
            result["signals"].append({
              "target":t,
              "source_id":str(r[0]),
              "source_url":r[1],
              "source_type":r[2],
              "title":r[3],
              "confidence_score":str(r[4]),
              "validation_status":r[5],
              "signal_terms":hits,
              "raw_payload":r[6]
            })

result["summary"]={
 "targets_checked":len(targets),
 "signals_found":len(result["signals"]),
 "progeny_like":sum(1 for s in result["signals"] if any(x in s["signal_terms"] for x in ["son","daughter","offspring","progeny","calf","calves"])),
 "valuation_like":sum(1 for s in result["signals"] if any(x in s["signal_terms"] for x in ["semen","embryo","sale","auction","sold","breeding rights","$","lot","catalog"]))
}

result["status"]="PASS"

(out/"P56G44_PROGENY_VALUATION_EXPANSION_LEDGER.json").write_text(
 json.dumps(result,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(result["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)

cur.close()
conn.close()
