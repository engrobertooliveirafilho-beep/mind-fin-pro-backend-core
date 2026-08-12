import os
import psycopg2
import json
from pathlib import Path

conn = psycopg2.connect(
    os.getenv("DATABASE_URL"),
    sslmode="require"
)

cur = conn.cursor()

cur.execute("""
select *
from p55a_pedigree_edges
""")

rows = cur.fetchall()

out = Path("reports/P5.6G29_PEDIGREE_RECONCILIATION")
out.mkdir(parents=True, exist_ok=True)

(Path(out / "P56G29A_ALL_PEDIGREE_EDGES.json")).write_text(
    json.dumps([list(r) for r in rows], indent=2, default=str),
    encoding="utf-8"
)

print("TOTAL_EDGES =", len(rows))

for r in rows:
    print(r)

cur.close()
conn.close()
