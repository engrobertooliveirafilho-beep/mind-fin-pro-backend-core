import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G33D_BUSHWACKER_ABBI_SOURCE_DEDUP"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

CANONICAL="df645e3f-d3c9-4eed-a876-d79d052a6f99"
DUPLICATES=[
 "4d508bfb-9e3f-4c20-860f-cf9ac6190e22",
 "f6c06b1f-28cd-4ca7-b371-3ed3840656a7",
 "930e9283-8289-40cd-a02f-b3bd46b015f7"
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "canonical_source_id":CANONICAL,
 "duplicate_source_ids":DUPLICATES,
 "phases":{},
 "status":"UNKNOWN"
}

# DRY RUN
cur.execute("""
select id, source_url, confidence_score, validation_status, raw_payload
from p55a_sources
where id = any(%s)
order by id
""",(DUPLICATES+[CANONICAL],))
before=cur.fetchall()
report["phases"]["dry_run"]=[list(map(str,r)) for r in before]

if len(before) != 4:
    report["status"]="BLOCKED"
    report["blocker"]="Expected 4 source records"
else:
    # ROLLBACK TEST
    try:
        cur.execute("BEGIN;")
        cur.execute("""
        update p55a_sources
        set validation_status='duplicate_candidate'
        where id = any(%s)
        """,(DUPLICATES,))
        cur.execute("""
        select id, validation_status
        from p55a_sources
        where id = any(%s)
        order by id
        """,(DUPLICATES+[CANONICAL],))
        rollback_snapshot=cur.fetchall()
        conn.rollback()
        report["phases"]["rollback_test"]=[list(map(str,r)) for r in rollback_snapshot]
        report["phases"]["rollback_test_status"]="PASS"

        # COMMIT
        cur.execute("""
        update p55a_sources
        set validation_status='duplicate_candidate'
        where id = any(%s)
        """,(DUPLICATES,))
        conn.commit()
        report["phases"]["commit_status"]="COMMIT_EXECUTED"

        # VALIDATE
        cur.execute("""
        select id, source_url, confidence_score, validation_status
        from p55a_sources
        where id = any(%s)
        order by id
        """,(DUPLICATES+[CANONICAL],))
        after=cur.fetchall()
        report["phases"]["validate"]=[list(map(str,r)) for r in after]

        status={str(r[0]):r[3] for r in after}
        ok = (
          status.get(CANONICAL) == "provisional" and
          all(status.get(x) == "duplicate_candidate" for x in DUPLICATES)
        )
        report["status"]="PASS" if ok else "REVIEW_REQUIRED"

    except Exception as e:
        conn.rollback()
        report["status"]="FAILED"
        report["error"]=repr(e)

(out/"P56G33D_BUSHWACKER_ABBI_SOURCE_DEDUP_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report,indent=2,ensure_ascii=False,default=str))

cur.close()
conn.close()
