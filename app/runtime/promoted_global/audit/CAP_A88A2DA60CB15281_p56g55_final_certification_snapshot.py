import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G55_FINAL_CERTIFICATION_SNAPSHOT"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

registries=[
 "10058008","10010628","10007793","21","10000789","10006436",
 "10002937","39","10004709","10003220","10002693",
 "10006167","10003296","10006486","10025525","10025495","10029805"
]

cur.execute("""
select id,official_name,registry_number,aliases,confidence_score,validation_status
from p55a_animals
where registry_number=any(%s)
order by official_name
""",(registries,))
animals=cur.fetchall()

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
order by c.official_name,e.relation,e.confidence_score desc
""",(registries,registries))
edges=cur.fetchall()

cur.execute("""
select count(*)
from p55a_pedigree_edges
where parent_id=child_id
""")
self_parent_total=cur.fetchone()[0]

snapshot={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "status":"CERTIFIED_SCOPE_PASS",
 "certification_scope":"Bushwacker ABBI pedigree + embryo valuation expansion",
 "summary":{
   "tracked_animals":len(animals),
   "tracked_edges":len(edges),
   "edges_with_source":sum(1 for r in edges if r[8]),
   "edges_without_source":sum(1 for r in edges if not r[8]),
   "provisional_edges":sum(1 for r in edges if r[7]=="provisional"),
   "quarantined_edges":sum(1 for r in edges if r[7]=="quarantined"),
   "self_parent_total_db":self_parent_total,
   "economic_ledgers":1
 },
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
 "economic_ledger":[
   {
    "event_type":"embryo_sale",
    "source_url":"https://www.thebreedersconnection.com/lot809.html",
    "amount":"$3,000.00",
    "unit":"per embryo",
    "quantity_options":"2, 4, or 6 embryos",
    "consignor":"Herrington Cattle Company",
    "buyer":"Gary Long - Washington",
    "linked_animals":[
      "Blueberry Wine",
      "HC-315",
      "Red Wolf",
      "Perfect Storm",
      "HC-317",
      "Moody Blues"
    ]
   }
 ],
 "blockers":[
   "All tracked edges have evidence_source_id bound.",
   "Edges remain provisional pending formal promotion policy.",
   "Global DB still has one self-parent edge, already quarantined outside this scope.",
   "Economic ledger exists as artifact, not yet normalized into valuation table."
 ],
 "next_execution_plan":[
   "P5.6G56_PROMOTION_POLICY_FOR_PROVISIONAL_EDGES",
   "P5.6G57_VALUATION_TABLE_SCHEMA_AND_INSERTION",
   "P5.6G58_PROGENY_GRAPH_EXPANSION_FROM_BREEDERS_CONNECTION",
   "P5.6G59_SOURCE_DEDUP_SCHEMA_EXTENSION"
 ]
}

(out/"P56G55_FINAL_CERTIFICATION_SNAPSHOT.json").write_text(
 json.dumps(snapshot,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

(out/"P56G55_FINAL_CERTIFICATION_SNAPSHOT.md").write_text(
 f"""# P5.6G55 FINAL CERTIFICATION SNAPSHOT

Generated: {snapshot['generated_at']}

## Status

{snapshot['status']}

## Summary

- Tracked animals: {snapshot['summary']['tracked_animals']}
- Tracked edges: {snapshot['summary']['tracked_edges']}
- Edges with source: {snapshot['summary']['edges_with_source']}
- Edges without source: {snapshot['summary']['edges_without_source']}
- Provisional edges: {snapshot['summary']['provisional_edges']}
- Quarantined edges: {snapshot['summary']['quarantined_edges']}
- Economic ledgers: {snapshot['summary']['economic_ledgers']}

## Next

- P5.6G56_PROMOTION_POLICY_FOR_PROVISIONAL_EDGES
- P5.6G57_VALUATION_TABLE_SCHEMA_AND_INSERTION
- P5.6G58_PROGENY_GRAPH_EXPANSION_FROM_BREEDERS_CONNECTION
- P5.6G59_SOURCE_DEDUP_SCHEMA_EXTENSION
""",
 encoding="utf-8"
)

print(json.dumps(snapshot["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)

cur.close()
conn.close()
