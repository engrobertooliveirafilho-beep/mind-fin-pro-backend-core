import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G31_POST_MUTATION_VALIDATION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

result={
  "mission":MISSION,
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "checks":{},
  "status":"UNKNOWN"
}

cur.execute("""
select count(*) from p55a_animals
where official_name in ('REINDEER MO','110')
or registry_number in ('10010628','10007793')
""")
result["checks"]["new_parent_entities"]=cur.fetchone()[0]

cur.execute("""
select count(*) from p55a_pedigree_edges e
left join p55a_animals c on c.id=e.child_id
where c.official_name='Bushwacker'
and e.validation_status='provisional'
""")
result["checks"]["bushwacker_provisional_edges"]=cur.fetchone()[0]

cur.execute("""
select e.relation,p.official_name,c.official_name,e.confidence_score,e.validation_status,e.evidence_source_id
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
left join p55a_animals c on c.id=e.child_id
where c.official_name='Bushwacker'
order by e.validation_status,e.relation,e.confidence_score desc
""")
edges=cur.fetchall()
result["bushwacker_edges"]=[list(map(str,r)) for r in edges]

cur.execute("""
select count(*) from p55a_pedigree_edges
where parent_id=child_id
""")
result["checks"]["self_parent_edges"]=cur.fetchone()[0]

cur.execute("""
select relation,count(*)
from p55a_pedigree_edges e
left join p55a_animals c on c.id=e.child_id
where c.official_name='Bushwacker'
and e.validation_status='provisional'
group by relation
""")
result["checks"]["bushwacker_provisional_by_relation"]={r[0]:r[1] for r in cur.fetchall()}

ok = (
  result["checks"]["new_parent_entities"] == 2 and
  result["checks"]["self_parent_edges"] == 1 and
  result["checks"]["bushwacker_provisional_by_relation"].get("sire",0) == 1 and
  result["checks"]["bushwacker_provisional_by_relation"].get("dam",0) == 1
)

result["status"]="PASS" if ok else "REVIEW_REQUIRED"

(out/"P56G31_POST_MUTATION_VALIDATION_SNAPSHOT.json").write_text(
  json.dumps(result,indent=2,ensure_ascii=False),
  encoding="utf-8"
)

print(json.dumps(result,indent=2,ensure_ascii=False))

cur.close()
conn.close()
