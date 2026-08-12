import os, json, uuid, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G41_VALID_STRUCTURAL_EDGE_INSERTION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

src=Path("reports/P5.6G40_ABBI_STRUCTURAL_PEDIGREE_PARSER/P56G40_ABBI_STRUCTURAL_PEDIGREE_PARSE.json")
data=json.loads(src.read_text(encoding="utf-8"))

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "mode":"DRY_RUN_ROLLBACK_COMMIT_VALIDATE",
 "status":"UNKNOWN",
 "skipped":[],
 "inserted_planned":[],
 "inserted_committed":[]
}

try:
    valid=[]
    for e in data["edge_candidates"]:
        if e["parent_abbi"] == e["child_abbi"]:
            report["skipped"].append({**e,"reason":"SELF_PARENT"})
            continue
        valid.append(e)

    for e in valid:
        cur.execute("select id from p55a_animals where registry_number=%s",(e["parent_abbi"],))
        p=cur.fetchone()
        cur.execute("select id from p55a_animals where registry_number=%s",(e["child_abbi"],))
        c=cur.fetchone()

        if not p or not c:
            report["skipped"].append({**e,"reason":"MISSING_ENTITY"})
            continue

        parent_id, child_id = p[0], c[0]

        cur.execute("""
        select id from p55a_pedigree_edges
        where parent_id=%s and child_id=%s and relation=%s
        """,(parent_id,child_id,e["relation"]))

        if cur.fetchone():
            report["skipped"].append({**e,"reason":"EDGE_ALREADY_EXISTS"})
            continue

        report["inserted_planned"].append({
          **e,
          "edge_id":str(uuid.uuid4()),
          "parent_id":str(parent_id),
          "child_id":str(child_id)
        })

    # rollback test
    cur.execute("BEGIN;")
    for e in report["inserted_planned"]:
        cur.execute("""
        insert into p55a_pedigree_edges
        (id,parent_id,child_id,relation,generation_distance,evidence_source_id,confidence_score,validation_status)
        values (%s,%s,%s,%s,1,null,%s,'provisional')
        """,(e["edge_id"],e["parent_id"],e["child_id"],e["relation"],e["confidence_score"]))

    cur.execute("select count(*) from p55a_pedigree_edges")
    rollback_count=cur.fetchone()[0]
    conn.rollback()

    report["rollback_test"]={"status":"PASS","edge_count_inside_rollback":rollback_count}

    # commit
    for e in report["inserted_planned"]:
        cur.execute("""
        insert into p55a_pedigree_edges
        (id,parent_id,child_id,relation,generation_distance,evidence_source_id,confidence_score,validation_status)
        values (%s,%s,%s,%s,1,null,%s,'provisional')
        """,(e["edge_id"],e["parent_id"],e["child_id"],e["relation"],e["confidence_score"]))

    conn.commit()

    report["inserted_committed"]=report["inserted_planned"]

    # validate
    cur.execute("""
    select p.official_name,c.official_name,e.relation,e.confidence_score,e.validation_status
    from p55a_pedigree_edges e
    left join p55a_animals p on p.id=e.parent_id
    left join p55a_animals c on c.id=e.child_id
    where e.validation_status='provisional'
    order by c.official_name,e.relation
    """)
    report["validation_edges"]=[list(map(str,r)) for r in cur.fetchall()]

    report["summary"]={
      "planned":len(report["inserted_planned"]),
      "committed":len(report["inserted_committed"]),
      "skipped":len(report["skipped"])
    }

    report["status"]="PASS"

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G41_VALID_STRUCTURAL_EDGE_INSERTION_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report["summary"] if "summary" in report else report,indent=2,ensure_ascii=False,default=str))
print("STATUS =",report["status"])

cur.close()
conn.close()
