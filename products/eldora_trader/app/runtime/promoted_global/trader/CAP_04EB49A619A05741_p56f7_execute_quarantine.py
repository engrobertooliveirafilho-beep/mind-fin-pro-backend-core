import os
import json
import psycopg2
from datetime import datetime, timezone

exec_sql = open("P56F6_QUARANTINE_EXECUTION_PLAN.sql", encoding="utf-8").read()

conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
cur = conn.cursor()

def counts():
    q = {}
    for table in ["p55a_animals","p55a_pedigree_edges","p55a_valuation_events"]:
        cur.execute(f"""
        SELECT validation_status, COUNT(*)
        FROM {table}
        GROUP BY validation_status
        ORDER BY validation_status
        """)
        q[table] = {str(k): v for k,v in cur.fetchall()}
    return q

before = counts()

cur.execute(exec_sql)
conn.commit()

after = counts()

snapshot = {
    "mission": "P5.6F7_QUARANTINE_EXECUTION_WITH_BEFORE_AFTER_DIFF",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "mode": "EXECUTED_LOGICAL_QUARANTINE_NO_DELETE",
    "before": before,
    "after": after,
    "rollback_file": "P56F6_QUARANTINE_ROLLBACK_PLAN.sql"
}

with open("P56F7_QUARANTINE_EXECUTION_DIFF.json","w",encoding="utf-8") as f:
    json.dump(snapshot,f,indent=2,ensure_ascii=False)

print(json.dumps(snapshot,indent=2,ensure_ascii=False))

conn.close()
