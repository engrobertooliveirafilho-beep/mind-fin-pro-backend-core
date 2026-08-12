import os, json, psycopg2, collections
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G33_SOURCE_DEDUP_CANONICALIZATION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

result={
  "mission":MISSION,
  "mode":"AUDIT_ONLY_NO_DATABASE_WRITE",
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "status":"UNKNOWN",
  "duplicate_groups":[],
  "canonicalization_plan":[],
  "summary":{}
}

cur.execute("""
select
  id,
  source_url,
  source_type,
  title,
  confidence_score,
  validation_status,
  created_at,
  raw_payload
from p55a_sources
where source_url is not null
order by source_url, confidence_score desc, created_at asc
""")

rows=cur.fetchall()
groups=collections.defaultdict(list)

for r in rows:
    groups[r[1]].append(r)

dups={k:v for k,v in groups.items() if len(v)>1}

for url,items in dups.items():
    candidates=[]
    for r in items:
        candidates.append({
          "id":str(r[0]),
          "source_url":r[1],
          "source_type":r[2],
          "title":r[3],
          "confidence_score":str(r[4]),
          "validation_status":r[5],
          "created_at":str(r[6]),
          "raw_payload":r[7]
        })

    sorted_items=sorted(
        candidates,
        key=lambda x: (
            -float(x["confidence_score"] or 0),
            x["created_at"]
        )
    )

    canonical=sorted_items[0]

    result["duplicate_groups"].append({
      "source_url":url,
      "count":len(candidates),
      "canonical_source_id":canonical["id"],
      "records":candidates
    })

    result["canonicalization_plan"].append({
      "source_url":url,
      "action":"KEEP_CANONICAL_MARK_OTHERS_DUPLICATE_CANDIDATE",
      "canonical_source_id":canonical["id"],
      "duplicate_source_ids":[x["id"] for x in sorted_items[1:]],
      "execution_status":"NOT_EXECUTED"
    })

result["summary"]={
  "total_sources":len(rows),
  "unique_urls":len(groups),
  "duplicate_url_groups":len(dups),
  "duplicate_records_total":sum(len(v)-1 for v in dups.values())
}

result["status"]="PASS_AUDIT_COMPLETE"

(out/"P56G33_SOURCE_DEDUP_CANONICALIZATION_AUDIT.json").write_text(
  json.dumps(result,indent=2,ensure_ascii=False,default=str),
  encoding="utf-8"
)

print(json.dumps(result["summary"],indent=2,ensure_ascii=False))

# foco Bushwacker ABBI
for g in result["duplicate_groups"]:
    if g["source_url"]=="http://members.americanbuckingbull.com/bulls.aspx?id=10058008":
        print("\nBUSHWACKER_ABBI_DUP_GROUP")
        print(json.dumps(g,indent=2,ensure_ascii=False,default=str))

cur.close()
conn.close()
