import os, json, psycopg2
from datetime import datetime, timezone

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
SELECT
    child.official_name,
    sire.official_name,
    dam.official_name
FROM p55a_reproduction_records r
LEFT JOIN p55a_animals child ON child.id=r.offspring_id
LEFT JOIN p55a_animals sire ON sire.id=r.sire_id
LEFT JOIN p55a_animals dam ON dam.id=r.dam_id
WHERE r.validation_status <> 'quarantined'
""")

graph={}

for child,sire,dam in cur.fetchall():
    if child not in graph:
        graph[child]={"sire":None,"dam":None,"parents":[]}
    if sire:
        graph[child]["sire"]=sire
        graph[child]["parents"].append(sire)
    if dam:
        graph[child]["dam"]=dam
        graph[child]["parents"].append(dam)

snapshot={
    "mission":"P5.6G1_REAL_GENETIC_GRAPH_REBUILD",
    "created_at":datetime.now(timezone.utc).isoformat(),
    "mode":"POST_QUARANTINE_REBUILD_NO_MUTATION",
    "nodes":len(set([x for child,v in graph.items() for x in [child]+v['parents']])),
    "edges":sum(len(v["parents"]) for v in graph.values()),
    "graph":graph
}

open("P56G1_REAL_GENETIC_GRAPH_REBUILD.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False))
print(json.dumps(snapshot,indent=2,ensure_ascii=False))

conn.close()
