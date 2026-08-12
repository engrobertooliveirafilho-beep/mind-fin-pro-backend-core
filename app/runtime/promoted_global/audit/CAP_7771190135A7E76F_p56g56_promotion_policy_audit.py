import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G56_PROMOTION_POLICY_FOR_PROVISIONAL_EDGES"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

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
 s.source_url,
 s.source_type,
 s.confidence_score source_confidence,
 s.validation_status source_status
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
left join p55a_animals c on c.id=e.child_id
left join p55a_sources s on s.id=e.evidence_source_id
where e.validation_status='provisional'
order by e.confidence_score desc
""")

edges=cur.fetchall()

tiers=[]
for r in edges:
    edge_conf=float(r[6] or 0)
    source_conf=float(r[11] or 0)
    source_type=str(r[10] or "")

    if edge_conf >= 90 and source_conf >= 80 and source_type in ["ABBI_LOCAL_HTML","COMMERCIAL_LOCAL_HTML","REAL_SEARCH_RESULT"]:
        tier="PROMOTION_READY_REVIEW"
    elif edge_conf >= 85 and r[8]:
        tier="KEEP_PROVISIONAL_STRONG"
    else:
        tier="KEEP_PROVISIONAL_WEAK"

    tiers.append({
      "edge_id":str(r[0]),
      "parent":r[1],
      "parent_abbi":r[2],
      "child":r[3],
      "child_abbi":r[4],
      "relation":r[5],
      "edge_confidence":str(r[6]),
      "source_id":str(r[8]) if r[8] else None,
      "source_url":r[9],
      "source_type":r[10],
      "source_confidence":str(r[11]),
      "source_status":r[12],
      "promotion_tier":tier
    })

summary={}
for t in tiers:
    summary[t["promotion_tier"]]=summary.get(t["promotion_tier"],0)+1

report={
 "mission":MISSION,
 "mode":"POLICY_AUDIT_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":summary,
 "edges":tiers,
 "decision":"NO_AUTOMATIC_PROMOTION_YET",
 "required_next":"P5.6G57_REVIEW_PROMOTION_READY_EDGES",
 "status":"PASS"
}

(out/"P56G56_PROMOTION_POLICY_AUDIT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(summary,indent=2,ensure_ascii=False))
print("OUTPUT =",out)

cur.close()
conn.close()
