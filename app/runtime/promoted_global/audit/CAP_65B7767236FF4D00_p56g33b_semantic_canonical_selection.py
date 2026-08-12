import os, json, psycopg2, collections, re
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G33B_SEMANTIC_CANONICAL_SOURCE_SELECTION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

GENETIC_TERMS=[
  "sire","dam","grandsire","granddam","pedigree","abbi#",
  "reindeer mo","bushwacker","offspring","son","daughter",
  "semen","embryo","sale","auction"
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

# sources referenciadas por edges
cur.execute("""
select distinct evidence_source_id
from p55a_pedigree_edges
where evidence_source_id is not null
""")
referenced={str(r[0]) for r in cur.fetchall()}

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

plans=[]
bushwacker_group=None

for url,items in groups.items():
    if len(items) <= 1:
        continue

    scored=[]
    for r in items:
        sid=str(r[0])
        raw=r[7] or {}
        snippet=str(raw.get("snippet","")).lower()
        query=str(raw.get("query","")).lower()
        title=str(r[3] or "").lower()
        text=" ".join([snippet,query,title])

        score=0
        reasons=[]

        if sid in referenced:
            score += 1000
            reasons.append("REFERENCED_BY_PEDIGREE_EDGE")

        conf=float(r[4] or 0)
        score += conf
        reasons.append(f"CONFIDENCE_{conf}")

        hits=[t for t in GENETIC_TERMS if t in text]
        score += len(hits) * 20
        if hits:
            reasons.append("GENETIC_TERMS:" + ",".join(hits))

        if "bodacious" in query and "10058008" in url:
            score -= 200
            reasons.append("QUERY_ENTITY_MISMATCH")

        scored.append({
          "id":sid,
          "source_url":url,
          "confidence_score":str(r[4]),
          "validation_status":r[5],
          "created_at":str(r[6]),
          "raw_payload":raw,
          "semantic_score":score,
          "reasons":reasons
        })

    scored=sorted(scored,key=lambda x:(-x["semantic_score"], x["created_at"]))
    canonical=scored[0]

    plan={
      "source_url":url,
      "count":len(scored),
      "canonical_source_id":canonical["id"],
      "duplicate_source_ids":[x["id"] for x in scored[1:]],
      "canonical_reasons":canonical["reasons"],
      "records":scored,
      "execution_status":"NOT_EXECUTED"
    }

    plans.append(plan)

    if url=="http://members.americanbuckingbull.com/bulls.aspx?id=10058008":
        bushwacker_group=plan

summary={
  "mission":MISSION,
  "mode":"AUDIT_ONLY_NO_DATABASE_WRITE",
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "duplicate_groups":len(plans),
  "referenced_sources":len(referenced),
  "status":"PASS"
}

(out/"P56G33B_SEMANTIC_CANONICAL_SELECTION_SUMMARY.json").write_text(
  json.dumps(summary,indent=2,ensure_ascii=False,default=str),
  encoding="utf-8"
)

(out/"P56G33B_SEMANTIC_CANONICAL_SELECTION_PLAN.json").write_text(
  json.dumps(plans,indent=2,ensure_ascii=False,default=str),
  encoding="utf-8"
)

if bushwacker_group:
    (out/"P56G33B_BUSHWACKER_ABBI_CANONICAL_GROUP.json").write_text(
      json.dumps(bushwacker_group,indent=2,ensure_ascii=False,default=str),
      encoding="utf-8"
    )

print(json.dumps(summary,indent=2,ensure_ascii=False))
print("\nBUSHWACKER_ABBI_GROUP")
print(json.dumps(bushwacker_group,indent=2,ensure_ascii=False,default=str))

cur.close()
conn.close()
