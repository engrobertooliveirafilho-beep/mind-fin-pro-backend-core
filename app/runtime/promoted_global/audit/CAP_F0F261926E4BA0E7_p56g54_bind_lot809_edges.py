import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G54_BIND_LOT809_EDGES"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

LOT809_URL="https://www.thebreedersconnection.com/lot809.html"

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "mode":"DRY_RUN_ROLLBACK_COMMIT_VALIDATE",
 "status":"UNKNOWN"
}

try:
    cur.execute("""
    select id, source_url, confidence_score, validation_status
    from p55a_sources
    where source_url=%s
    order by confidence_score desc nulls last
    limit 1
    """,(LOT809_URL,))
    row=cur.fetchone()

    if not row:
        report["status"]="BLOCKED"
        report["blocker"]="LOT809 source not found in p55a_sources"
    else:
        source_id=str(row[0])
        report["lot809_source_id"]=source_id

        cur.execute("""
        select e.id,p.official_name,c.official_name,e.relation
        from p55a_pedigree_edges e
        left join p55a_animals p on p.id=e.parent_id
        left join p55a_animals c on c.id=e.child_id
        where e.evidence_source_id is null
          and (
            (p.registry_number='10006167' and c.registry_number='10025495') or
            (p.registry_number='10003296' and c.registry_number='10025495') or
            (p.registry_number='10006486' and c.registry_number='10029805') or
            (p.registry_number='10025525' and c.registry_number='10029805')
          )
        """)
        edges=cur.fetchall()

        report["edges_found"]=[
          {"edge_id":str(r[0]),"parent":r[1],"child":r[2],"relation":r[3]} for r in edges
        ]

        # rollback
        cur.execute("BEGIN;")
        for r in edges:
            cur.execute("""
            update p55a_pedigree_edges
            set evidence_source_id=%s
            where id=%s and evidence_source_id is null
            """,(source_id,r[0]))
        conn.rollback()

        # commit
        for r in edges:
            cur.execute("""
            update p55a_pedigree_edges
            set evidence_source_id=%s
            where id=%s and evidence_source_id is null
            """,(source_id,r[0]))
        conn.commit()

        report["summary"]={
          "edges_bound":len(edges),
          "source_id":source_id
        }
        report["status"]="PASS"

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G54_BIND_LOT809_EDGES_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report.get("summary",report),indent=2,ensure_ascii=False,default=str))
print("STATUS =",report["status"])

cur.close()
conn.close()
