import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G38_BUSHWACKER_GRAPH_SNAPSHOT_G0_G2"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

registry_targets=["10058008","10010628","10007793","21","10000789","10006436","10002937","39"]

cur.execute("""
select id, official_name, registry_number, aliases, confidence_score, validation_status
from p55a_animals
where registry_number=any(%s)
order by registry_number
""",(registry_targets,))

animals=cur.fetchall()

cur.execute("""
select
  p.official_name parent,
  p.registry_number parent_abbi,
  c.official_name child,
  c.registry_number child_abbi,
  e.relation,
  e.confidence_score,
  e.validation_status,
  e.evidence_source_id
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
left join p55a_animals c on c.id=e.child_id
where c.registry_number=any(%s)
   or p.registry_number=any(%s)
order by c.official_name,e.relation,e.confidence_score desc
""",(registry_targets,registry_targets))

edges=cur.fetchall()

snapshot={
  "mission":MISSION,
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "status":"PASS",
  "scope":"Bushwacker G0-G2",
  "animals":[
    {
      "id":str(r[0]),
      "official_name":r[1],
      "registry_number":r[2],
      "aliases":r[3],
      "confidence_score":str(r[4]),
      "validation_status":r[5]
    } for r in animals
  ],
  "edges":[
    {
      "parent":r[0],
      "parent_abbi":r[1],
      "child":r[2],
      "child_abbi":r[3],
      "relation":r[4],
      "confidence_score":str(r[5]),
      "validation_status":r[6],
      "evidence_source_id":str(r[7]) if r[7] else None
    } for r in edges
  ],
  "summary":{
    "animal_count":len(animals),
    "edge_count":len(edges),
    "provisional_edges":sum(1 for r in edges if r[6]=="provisional"),
    "quarantined_edges":sum(1 for r in edges if r[6]=="quarantined")
  }
}

(out/"P56G38_BUSHWACKER_GRAPH_SNAPSHOT_G0_G2.json").write_text(
 json.dumps(snapshot,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(snapshot["summary"],indent=2,ensure_ascii=False))
print()
for e in snapshot["edges"]:
    print(e["validation_status"], e["parent"], "->", e["child"], e["relation"], e["confidence_score"])

cur.close()
conn.close()
