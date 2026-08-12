import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G58_FINAL_POST_PROMOTION_AUDIT"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

registries=[
 "10058008","10010628","10007793","21","10000789","10006436",
 "10002937","39","10004709","10003220","10002693",
 "10006167","10003296","10006486","10025525","10025495","10029805"
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

cur.execute("""
select
 e.id,
 p.official_name parent,
 p.registry_number parent_abbi,
 c.official_name child,
 c.registry_number child_abbi,
 e.relation,
 e.confidence_score,
 e.validation_status,
 e.evidence_source_id,
 s.source_url
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
left join p55a_animals c on c.id=e.child_id
left join p55a_sources s on s.id=e.evidence_source_id
where p.registry_number=any(%s)
   or c.registry_number=any(%s)
order by e.validation_status,c.official_name,e.relation
""",(registries,registries))
edges=cur.fetchall()

cur.execute("""
select count(*)
from p55a_pedigree_edges
where parent_id=child_id
""")
self_parent_total=cur.fetchone()[0]

summary={
 "tracked_edges":len(edges),
 "reliable_edges":sum(1 for r in edges if r[7]=="reliable"),
 "provisional_edges":sum(1 for r in edges if r[7]=="provisional"),
 "quarantined_edges":sum(1 for r in edges if r[7]=="quarantined"),
 "edges_with_source":sum(1 for r in edges if r[8]),
 "edges_without_source":sum(1 for r in edges if not r[8]),
 "self_parent_total_db":self_parent_total
}

status="CERTIFIED_PASS" if (
 summary["tracked_edges"]==17 and
 summary["reliable_edges"]==9 and
 summary["provisional_edges"]==8 and
 summary["edges_without_source"]==0
) else "REVIEW_REQUIRED"

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "status":status,
 "summary":summary,
 "edges":[
   {
    "edge_id":str(r[0]),
    "parent":r[1],
    "parent_abbi":r[2],
    "child":r[3],
    "child_abbi":r[4],
    "relation":r[5],
    "confidence_score":str(r[6]),
    "validation_status":r[7],
    "evidence_source_id":str(r[8]) if r[8] else None,
    "source_url":r[9]
   } for r in edges
 ],
 "next_execution_plan":[
   "P5.6G59_VALUATION_TABLE_SCHEMA_AND_INSERTION",
   "P5.6G60_PROGENY_GRAPH_EXPANSION",
   "P5.6G61_SOURCE_DEDUP_SCHEMA_EXTENSION"
 ]
}

(out/"P56G58_FINAL_POST_PROMOTION_AUDIT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(summary,indent=2,ensure_ascii=False))
print("STATUS =",status)
print("OUTPUT =",out)

cur.close()
conn.close()
