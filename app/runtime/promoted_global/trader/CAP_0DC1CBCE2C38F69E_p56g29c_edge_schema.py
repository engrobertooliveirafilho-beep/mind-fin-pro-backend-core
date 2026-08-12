import os
import psycopg2

conn = psycopg2.connect(
    os.getenv("DATABASE_URL"),
    sslmode="require"
)

cur = conn.cursor()

cur.execute("""
select
    ordinal_position,
    column_name,
    data_type
from information_schema.columns
where table_name='p55a_pedigree_edges'
order by ordinal_position
""")

for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
