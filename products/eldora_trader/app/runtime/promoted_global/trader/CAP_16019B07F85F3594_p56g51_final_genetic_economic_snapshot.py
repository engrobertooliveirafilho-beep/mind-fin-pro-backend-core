import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G51_FINAL_GENETIC_ECONOMIC_GRAPH_SNAPSHOT"
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
select id,official_name,registry_number,aliases,confidence_score,validation_status
from p55a_animals
where registry_number=any(%s)
order by official_name
""",(registries,))
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
""",(registries,registries))
edges=cur.fetchall()

snapshot={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "status":"PASS",
 "summary":{
   "tracked_animals":len(animals),
   "tracked_edges":len(edges),
   "provisional_edges":sum(1 for r in edges if r[6]=="provisional"),
   "quarantined_edges":sum(1 for r in edges if r[6]=="quarantined"),
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
 "economic_graph":[
   {
    "event_type":"embryo_sale",
    "lot":"Lot #809",
    "amount":"$3,000.00",
    "unit":"per embryo",
    "quantity_options":"2, 4, or 6 embryos",
    "source_url":"https://www.thebreedersconnection.com/lot809.html",
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
 "next_recommended":[
   "P5.6G52_SOURCE_EVIDENCE_BINDING_FOR_NULL_EDGES",
   "P5.6G53_PROGENY_GRAPH_EXPANSION_FROM_BREEDERS_CONNECTION",
   "P5.6G54_VALUATION_TABLE_INTEGRATION"
 ]
}

(out/"P56G51_FINAL_GENETIC_ECONOMIC_GRAPH_SNAPSHOT.json").write_text(
 json.dumps(snapshot,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(snapshot["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)

cur.close()
conn.close()
