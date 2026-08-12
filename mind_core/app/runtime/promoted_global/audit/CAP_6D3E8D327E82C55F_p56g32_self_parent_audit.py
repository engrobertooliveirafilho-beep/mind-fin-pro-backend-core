import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G32_SELF_PARENT_QUARANTINE_VALIDATION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

result={
  "mission":MISSION,
  "mode":"AUDIT_ONLY_NO_DATABASE_WRITE",
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "status":"UNKNOWN",
  "self_parent_edges":[],
  "mutation_plan":[]
}

cur.execute("""
select
  e.id,
  e.relation,
  e.validation_status,
  e.confidence_score,
  e.evidence_source_id,
  p.official_name,
  p.registry_number,
  e.created_at
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
where e.parent_id=e.child_id
order by e.created_at asc
""")

rows=cur.fetchall()

for r in rows:
    edge={
      "edge_id":str(r[0]),
      "relation":r[1],
      "validation_status":r[2],
      "confidence_score":str(r[3]),
      "evidence_source_id":str(r[4]) if r[4] else None,
      "animal_name":r[5],
      "registry_number":r[6],
      "created_at":str(r[7])
    }
    result["self_parent_edges"].append(edge)

    result["mutation_plan"].append({
      "action":"ENSURE_QUARANTINED",
      "edge_id":edge["edge_id"],
      "current_status":edge["validation_status"],
      "target_status":"quarantined",
      "reason":"SELF_PARENT_INVALID_PEDIGREE_EDGE"
    })

if len(rows)==0:
    result["status"]="PASS_NO_SELF_PARENT"
elif all(r[2]=="quarantined" for r in rows):
    result["status"]="PASS_ALREADY_QUARANTINED"
else:
    result["status"]="ACTION_REQUIRED"

(out/"P56G32_SELF_PARENT_AUDIT.json").write_text(
  json.dumps(result,indent=2,ensure_ascii=False),
  encoding="utf-8"
)

print(json.dumps(result,indent=2,ensure_ascii=False))

cur.close()
conn.close()
