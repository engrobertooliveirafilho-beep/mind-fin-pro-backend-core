import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G57_PROMOTE_CERTIFIED_ABBI_PEDIGREE_EDGES"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

EDGE_IDS=[
 "c206fb80-a043-42aa-ba57-52ae26ddace5",
 "56169745-68c6-49ad-bb31-13c60b5b9677",
 "6b003181-ec3b-42cf-9128-301faf0ef207",
 "b8148188-a465-4410-aed8-18bd15a720e7",
 "27de441d-fd9b-4798-ad28-41277643fee5",
 "0b5e56e8-6210-48ff-81e0-9ce1dd1f4341",
 "1f1962dd-d37d-4bc2-9309-81151c568c1b",
 "96679007-ae33-429d-98bf-641a2a262f0c",
 "0197da50-2146-4cd1-bfec-e5ba7a8be7e1"
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "mode":"DRY_RUN_ROLLBACK_COMMIT_VALIDATE",
 "target_edges":len(EDGE_IDS),
 "status":"UNKNOWN"
}

try:
    cur.execute("""
    select
      e.id,
      p.official_name parent,
      c.official_name child,
      e.relation,
      e.confidence_score,
      e.validation_status,
      e.evidence_source_id
    from p55a_pedigree_edges e
    left join p55a_animals p on p.id=e.parent_id
    left join p55a_animals c on c.id=e.child_id
    where e.id::text = any(%s)
    order by c.official_name,e.relation
    """,(EDGE_IDS,))
    before=cur.fetchall()

    blockers=[]
    if len(before) != len(EDGE_IDS):
        blockers.append("EDGE_COUNT_MISMATCH")

    for r in before:
        if str(r[5])!="provisional":
            blockers.append(f"EDGE_NOT_PROVISIONAL:{r[0]}")
        if not r[6]:
            blockers.append(f"MISSING_EVIDENCE_SOURCE:{r[0]}")
        if float(r[4] or 0) < 90:
            blockers.append(f"LOW_CONFIDENCE:{r[0]}")

    report["before"]=[list(map(str,r)) for r in before]
    report["blockers"]=blockers

    if blockers:
        report["status"]="BLOCKED"
    else:
        # rollback test
        cur.execute("BEGIN;")
        cur.execute("""
        update p55a_pedigree_edges
        set validation_status='reliable'
        where id::text = any(%s)
        """,(EDGE_IDS,))
        cur.execute("""
        select count(*)
        from p55a_pedigree_edges
        where id::text = any(%s)
          and validation_status='reliable'
        """,(EDGE_IDS,))
        rollback_promoted=cur.fetchone()[0]
        conn.rollback()

        report["rollback_test"]={
          "promoted_inside_rollback":rollback_promoted,
          "status":"PASS" if rollback_promoted==len(EDGE_IDS) else "REVIEW_REQUIRED"
        }

        if rollback_promoted != len(EDGE_IDS):
            report["status"]="BLOCKED"
            report["blockers"].append("ROLLBACK_TEST_COUNT_MISMATCH")
        else:
            cur.execute("""
            update p55a_pedigree_edges
            set validation_status='reliable'
            where id::text = any(%s)
            """,(EDGE_IDS,))
            conn.commit()

            cur.execute("""
            select
              e.id,
              p.official_name parent,
              c.official_name child,
              e.relation,
              e.confidence_score,
              e.validation_status,
              e.evidence_source_id
            from p55a_pedigree_edges e
            left join p55a_animals p on p.id=e.parent_id
            left join p55a_animals c on c.id=e.child_id
            where e.id::text = any(%s)
            order by c.official_name,e.relation
            """,(EDGE_IDS,))
            after=cur.fetchall()

            report["after"]=[list(map(str,r)) for r in after]
            report["summary"]={
              "edges_targeted":len(EDGE_IDS),
              "edges_promoted":sum(1 for r in after if r[5]=="reliable"),
              "edges_with_source":sum(1 for r in after if r[6])
            }
            report["status"]="PASS"

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G57_PROMOTE_CERTIFIED_ABBI_PEDIGREE_EDGES_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report.get("summary",report),indent=2,ensure_ascii=False,default=str))
print("STATUS =",report["status"])

cur.close()
conn.close()
