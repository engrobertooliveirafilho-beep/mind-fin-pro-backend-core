import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G59A_VALUATION_SCHEMA_AUDIT"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

cur.execute("""
select ordinal_position,column_name,data_type,is_nullable
from information_schema.columns
where table_name='p55a_valuation_events'
order by ordinal_position
""")

cols=cur.fetchall()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "table":"p55a_valuation_events",
 "columns":[
   {
    "ordinal_position":r[0],
    "column_name":r[1],
    "data_type":r[2],
    "is_nullable":r[3]
   } for r in cols
 ],
 "status":"PASS" if cols else "TABLE_NOT_FOUND"
}

(out/"P56G59A_VALUATION_SCHEMA_AUDIT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

for c in report["columns"]:
    print(c)

cur.close()
conn.close()
