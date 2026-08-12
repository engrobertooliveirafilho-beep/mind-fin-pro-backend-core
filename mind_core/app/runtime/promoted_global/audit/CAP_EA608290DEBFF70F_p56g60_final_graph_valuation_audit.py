import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G60_FINAL_GRAPH_VALUATION_AUDIT"
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
 e.validation_status,
 count(*)
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
left join p55a_animals c on c.id=e.child_id
where p.registry_number=any(%s)
   or c.registry_number=any(%s)
group by e.validation_status
order by e.validation_status
""",(registries,registries))
edge_status=dict(cur.fetchall())

cur.execute("""
select count(*)
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
left join p55a_animals c on c.id=e.child_id
where (p.registry_number=any(%s) or c.registry_number=any(%s))
  and e.evidence_source_id is null
""",(registries,registries))
null_sources=cur.fetchone()[0]

cur.execute("""
select count(*)
from p55a_valuation_events
where source_id in (
  select id from p55a_sources
  where source_url='https://www.thebreedersconnection.com/lot809.html'
)
""")
lot809_valuation_events=cur.fetchone()[0]

cur.execute("""
select id,event_type,amount,embryo_price,currency,buyer,seller,auction_name,validation_status
from p55a_valuation_events
where source_id in (
  select id from p55a_sources
  where source_url='https://www.thebreedersconnection.com/lot809.html'
)
order by created_at desc
limit 5
""")
valuation_rows=cur.fetchall()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "status":"CERTIFIED_PASS" if null_sources==0 and lot809_valuation_events>=1 else "REVIEW_REQUIRED",
 "summary":{
   "reliable_edges":edge_status.get("reliable",0),
   "provisional_edges":edge_status.get("provisional",0),
   "quarantined_edges":edge_status.get("quarantined",0),
   "edges_without_source":null_sources,
   "lot809_valuation_events":lot809_valuation_events
 },
 "valuation_sample":[
   {
    "id":str(r[0]),
    "event_type":r[1],
    "amount":str(r[2]),
    "embryo_price":str(r[3]),
    "currency":r[4],
    "buyer":r[5],
    "seller":r[6],
    "auction_name":r[7],
    "validation_status":r[8]
   } for r in valuation_rows
 ],
 "next_recommended":[
   "P5.6G61_PROGENY_GRAPH_EXPANSION",
   "P5.6G62_VALUATION_PROMOTION_POLICY",
   "P5.6G63_SOURCE_DEDUP_SCHEMA_EXTENSION"
 ]
}

(out/"P56G60_FINAL_GRAPH_VALUATION_AUDIT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report["summary"],indent=2,ensure_ascii=False))
print("STATUS =",report["status"])
print("OUTPUT =",out)

cur.close()
conn.close()
