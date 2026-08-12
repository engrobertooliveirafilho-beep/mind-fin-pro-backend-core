import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G52_SOURCE_EVIDENCE_BINDING_AUDIT"
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
 e.evidence_source_id
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
left join p55a_animals c on c.id=e.child_id
where (p.registry_number=any(%s) or c.registry_number=any(%s))
order by c.official_name,e.relation
""",(registries,registries))

edges=cur.fetchall()

null_edges=[]
bound_edges=[]

for r in edges:
    item={
      "edge_id":str(r[0]),
      "parent":r[1],
      "parent_abbi":r[2],
      "child":r[3],
      "child_abbi":r[4],
      "relation":r[5],
      "confidence_score":str(r[6]),
      "validation_status":r[7],
      "evidence_source_id":str(r[8]) if r[8] else None
    }
    if r[8]:
        bound_edges.append(item)
    else:
        null_edges.append(item)

# procurar fontes por URL ABBI/lot provável
binding_candidates=[]

for e in null_edges:
    urls=[
      f"http://members.americanbuckingbull.com/bulls.aspx?id={e['child_abbi']}",
      f"http://members.americanbuckingbull.com/bulls.aspx?id={e['parent_abbi']}"
    ]

    found=[]
    for url in urls:
        cur.execute("""
        select id, source_url, confidence_score, validation_status, raw_payload
        from p55a_sources
        where source_url=%s
        order by confidence_score desc nulls last, created_at asc
        limit 5
        """,(url,))
        for s in cur.fetchall():
            found.append({
              "source_id":str(s[0]),
              "source_url":s[1],
              "confidence_score":str(s[2]),
              "validation_status":s[3],
              "raw_payload":s[4]
            })

    binding_candidates.append({
      "edge":e,
      "candidate_sources":found,
      "recommended_source_id":found[0]["source_id"] if found else None,
      "status":"BINDABLE" if found else "NO_SOURCE_FOUND"
    })

report={
 "mission":MISSION,
 "mode":"AUDIT_ONLY_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":{
   "tracked_edges":len(edges),
   "bound_edges":len(bound_edges),
   "null_evidence_edges":len(null_edges),
   "bindable":sum(1 for x in binding_candidates if x["status"]=="BINDABLE"),
   "no_source_found":sum(1 for x in binding_candidates if x["status"]=="NO_SOURCE_FOUND")
 },
 "bound_edges":bound_edges,
 "null_edges":null_edges,
 "binding_candidates":binding_candidates,
 "status":"PASS"
}

(out/"P56G52_SOURCE_EVIDENCE_BINDING_AUDIT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)

cur.close()
conn.close()
