import os
import psycopg2

conn = psycopg2.connect(
    os.getenv("DATABASE_URL"),
    sslmode="require"
)

cur = conn.cursor()

cur.execute("""
select
    validation_status,
    count(*)
from p55a_animals
group by validation_status
order by count(*) desc
""")

print("VALIDATION_STATUS")
for r in cur.fetchall():
    print(r)

cur.execute("""
select
    animal_type,
    count(*)
from p55a_animals
group by animal_type
order by count(*) desc
""")

print()
print("ANIMAL_TYPE")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
