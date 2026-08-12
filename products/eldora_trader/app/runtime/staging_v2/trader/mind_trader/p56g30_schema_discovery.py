import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

OUT=Path("reports/P5.6G30_CONTROLLED_PEDIGREE_MUTATION")
OUT.mkdir(parents=True, exist_ok=True)

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

cur.execute("""
select table_schema, table_name
from information_schema.tables
where table_schema not in ('pg_catalog','information_schema')
order by table_schema, table_name;
""")
tables=cur.fetchall()

cur.execute("""
select table_schema, table_name, column_name, data_type
from information_schema.columns
where table_schema not in ('pg_catalog','information_schema')
order by table_schema, table_name, ordinal_position;
""")
cols=cur.fetchall()

report={
  "STATUS":"P5.6G30_SCHEMA_DISCOVERY_COMPLETED",
  "TABLES":[{"schema":s,"table":t} for s,t in tables],
  "COLUMNS":[{"schema":s,"table":t,"column":c,"type":dt} for s,t,c,dt in cols],
  "NEXT":"IDENTIFY_ANIMAL_AND_RELATIONSHIP_TABLES",
  "generated_at":datetime.now(timezone.utc).isoformat()
}

(OUT/"p56g30_schema_discovery.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")

cur.close()
conn.close()

print(json.dumps({
  "STATUS":report["STATUS"],
  "TABLES_COUNT":len(tables),
  "COLUMNS_COUNT":len(cols),
  "NEXT":report["NEXT"]
}, indent=2))
