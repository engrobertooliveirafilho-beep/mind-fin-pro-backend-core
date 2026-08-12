import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G43_FINAL_EXPANDED_GRAPH_HANDOFF"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

registry_targets=[
 "10058008","10010628","10007793","21","10000789",
 "10006436","10002937","39","10004709","10003220","10002693"
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

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
where p.registry_number=any(%s)
   or c.registry_number=any(%s)
order by c.official_name,e.relation,e.confidence_score desc
""",(registry_targets,registry_targets))
edges=cur.fetchall()

cur.execute("""
select count(*) from p55a_pedigree_edges
where parent_id=child_id
""")
self_parent_count=cur.fetchone()[0]

handoff={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "status":"PASS",
 "project_state":{
   "latest_completed":[
     "P5.6G30_CONTROLLED_PEDIGREE_MUTATION_EXECUTED",
     "P5.6G31_POST_MUTATION_VALIDATION_PASS",
     "P5.6G32_SELF_PARENT_ALREADY_QUARANTINED",
     "P5.6G33_SOURCE_DEDUP_EXTERNAL_LEDGER_CREATED",
     "P5.6G37_PARENT_EXPANSION_EXECUTED",
     "P5.6G38_GRAPH_SNAPSHOT_PASS",
     "P5.6G39_ABBI_MAX_EXPANSION_PASS",
     "P5.6G40_STRUCTURAL_PARSER_PASS",
     "P5.6G41_VALID_EDGE_INSERTION_PASS",
     "P5.6G42_PENDING_EDGES_ALREADY_EXIST_PASS"
   ],
   "current_focus":"Expanded Bushwacker ABBI pedigree graph",
   "next_recommended":"P5.6G44_PROGENY_AND_VALUATION_EXPANSION"
 },
 "graph_snapshot":{
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
   ]
 },
 "summary":{
   "tracked_animals":len(animals),
   "tracked_edges":len(edges),
   "provisional_edges":sum(1 for r in edges if r[6]=="provisional"),
   "quarantined_edges":sum(1 for r in edges if r[6]=="quarantined"),
   "self_parent_edges_total_db":self_parent_count
 },
 "known_blockers":[
   "Some structural edges still have evidence_source_id=null",
   "Source dedup cannot be committed because p55a_sources has no dedup_status/canonical_source_id column",
   "Self-parent exists globally but is already quarantined",
   "Dam of MO 110 missing in public ABBI page",
   "Further expansion should avoid regex token parser and use structural ABBI parser only"
 ],
 "next_actions":[
   "Add evidence_source_id binding for newly inserted G37/G41/G42 edges",
   "Create canonical source metadata table or columns before dedup mutation",
   "Run progeny discovery for Bushwacker and REINDEER",
   "Run valuation expansion for semen, embryo, auctions and offspring sales",
   "Generate graph depth/width metrics after evidence binding"
 ]
}

(out/"P56G43_FINAL_EXPANDED_GRAPH_HANDOFF.json").write_text(
 json.dumps(handoff,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

(out/"P56G43_FINAL_EXPANDED_GRAPH_HANDOFF.md").write_text(
 "# P5.6G43 FINAL EXPANDED GRAPH HANDOFF\n\n"
 f"Generated: {handoff['generated_at']}\n\n"
 "## Summary\n\n"
 f"- Tracked animals: {handoff['summary']['tracked_animals']}\n"
 f"- Tracked edges: {handoff['summary']['tracked_edges']}\n"
 f"- Provisional edges: {handoff['summary']['provisional_edges']}\n"
 f"- Quarantined edges: {handoff['summary']['quarantined_edges']}\n"
 f"- Self-parent edges total DB: {handoff['summary']['self_parent_edges_total_db']}\n\n"
 "## Next Recommended\n\nP5.6G44_PROGENY_AND_VALUATION_EXPANSION\n",
 encoding="utf-8"
)

print(json.dumps(handoff["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =", out)

cur.close()
conn.close()
