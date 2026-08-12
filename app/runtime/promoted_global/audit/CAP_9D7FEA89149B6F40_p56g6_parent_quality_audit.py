import os, psycopg2

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
SELECT official_name, validation_status, confidence_score
FROM p55a_animals
WHERE official_name IN (
'TBB 8460',
'Showtime',
'JATT 4702 Original Breeder',
'J31A Bodacious DAM',
'Bodacious Daughter Lot',
'E40 Black',
'GLC687'
)
ORDER BY official_name
""")

for r in cur.fetchall():
    print(r)

conn.close()
