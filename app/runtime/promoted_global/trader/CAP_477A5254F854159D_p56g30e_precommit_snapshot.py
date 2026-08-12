import os
import psycopg2

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur = conn.cursor()

cur.execute("""
select count(*)
from p55a_pedigree_edges
where validation_status='reliable'
""")
print("RELIABLE_EDGES_BEFORE=", cur.fetchone()[0])

cur.execute("""
select count(*)
from p55a_animals
where official_name in ('REINDEER MO','110')
   or registry_number in ('10010628','10007793')
""")
print("NEW_PARENT_ENTITIES_BEFORE=", cur.fetchone()[0])

cur.close()
conn.close()
