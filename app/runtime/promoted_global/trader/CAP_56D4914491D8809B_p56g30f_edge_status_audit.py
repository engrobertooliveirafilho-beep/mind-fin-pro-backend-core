import os
import psycopg2

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur = conn.cursor()

cur.execute("""
select
    validation_status,
    count(*)
from p55a_pedigree_edges
group by validation_status
order by count(*) desc
""")

for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
