import os, json, uuid, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G42_MISSING_ENTITIES_AND_PENDING_EDGES"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

missing_entities=[
  {"official_name":"AN 11","registry_number":"10004709","confidence_score":85},
  {"official_name":"ORIGINAL JR","registry_number":"10003220","confidence_score":85},
  {"official_name":"JR 3","registry_number":"10002693","confidence_score":85}
]

pending_edges=[
  {"parent_abbi":"10006436","child_abbi":"10004709","relation":"sire","confidence_score":90},
  {"parent_abbi":"21","child_abbi":"10004709","relation":"dam","confidence_score":90},
  {"parent_abbi":"10003220","child_abbi":"10002937","relation":"sire","confidence_score":90},
  {"parent_abbi":"10002693","child_abbi":"10002937","relation":"dam","confidence_score":90},
  {"parent_abbi":"39","child_abbi":"10003220","relation":"sire","confidence_score":90},
  {"parent_abbi":"39","child_abbi":"10002693","relation":"sire","confidence_score":90},
  {"parent_abbi":"10004709","child_abbi":"10010628","relation":"dam","confidence_score":90}
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "mode":"DRY_RUN_ROLLBACK_COMMIT_VALIDATE",
 "created_entities":[],
 "created_edges":[],
 "skipped":[],
 "status":"UNKNOWN"
}

try:
    # Create missing entities if absent
    for ent in missing_entities:
        cur.execute("select id from p55a_animals where registry_number=%s",(ent["registry_number"],))
        row=cur.fetchone()
        if row:
            report["skipped"].append({**ent,"reason":"ENTITY_ALREADY_EXISTS"})
            ent["id"]=str(row[0])
        else:
            ent["id"]=str(uuid.uuid4())
            report["created_entities"].append(ent)

    def build_sql():
        statements=[]
        for ent in report["created_entities"]:
            statements.append((
              "insert into p55a_animals "
              "(id,official_name,registry_number,animal_type,confidence_score,validation_status,notes) "
              "values (%s,%s,%s,'bull',%s,'provisional','Created from P5.6G42 ABBI structural expansion.')",
              (ent["id"],ent["official_name"],ent["registry_number"],ent["confidence_score"])
            ))
        return statements

    # rollback entity test
    cur.execute("BEGIN;")
    for sql,args in build_sql():
        cur.execute(sql,args)
    conn.rollback()

    # commit entities
    for sql,args in build_sql():
        cur.execute(sql,args)
    conn.commit()

    # resolve all entities
    cur.execute("select id,registry_number,official_name from p55a_animals")
    animals={r[1]:{"id":str(r[0]),"name":r[2]} for r in cur.fetchall() if r[1]}

    # plan edges
    edge_inserts=[]
    for e in pending_edges:
        p=animals.get(e["parent_abbi"])
        c=animals.get(e["child_abbi"])

        if not p or not c:
            report["skipped"].append({**e,"reason":"MISSING_PARENT_OR_CHILD"})
            continue

        if p["id"] == c["id"]:
            report["skipped"].append({**e,"reason":"SELF_PARENT"})
            continue

        cur.execute("""
        select id from p55a_pedigree_edges
        where parent_id=%s and child_id=%s and relation=%s
        """,(p["id"],c["id"],e["relation"]))

        if cur.fetchone():
            report["skipped"].append({**e,"reason":"EDGE_ALREADY_EXISTS"})
            continue

        edge={
          **e,
          "edge_id":str(uuid.uuid4()),
          "parent_id":p["id"],
          "child_id":c["id"],
          "parent":p["name"],
          "child":c["name"]
        }
        edge_inserts.append(edge)

    # rollback edge test
    cur.execute("BEGIN;")
    for e in edge_inserts:
        cur.execute("""
        insert into p55a_pedigree_edges
        (id,parent_id,child_id,relation,generation_distance,evidence_source_id,confidence_score,validation_status)
        values (%s,%s,%s,%s,1,null,%s,'provisional')
        """,(e["edge_id"],e["parent_id"],e["child_id"],e["relation"],e["confidence_score"]))
    conn.rollback()

    # commit edges
    for e in edge_inserts:
        cur.execute("""
        insert into p55a_pedigree_edges
        (id,parent_id,child_id,relation,generation_distance,evidence_source_id,confidence_score,validation_status)
        values (%s,%s,%s,%s,1,null,%s,'provisional')
        """,(e["edge_id"],e["parent_id"],e["child_id"],e["relation"],e["confidence_score"]))
        report["created_edges"].append(e)

    conn.commit()

    # validate
    cur.execute("""
    select p.official_name,c.official_name,e.relation,e.confidence_score,e.validation_status
    from p55a_pedigree_edges e
    left join p55a_animals p on p.id=e.parent_id
    left join p55a_animals c on c.id=e.child_id
    where c.registry_number in ('10004709','10002937','10003220','10002693','10010628')
    order by c.official_name,e.relation
    """)
    report["validation_edges"]=[list(map(str,r)) for r in cur.fetchall()]

    report["summary"]={
      "entities_created":len(report["created_entities"]),
      "edges_created":len(report["created_edges"]),
      "skipped":len(report["skipped"])
    }
    report["status"]="PASS"

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G42_MISSING_ENTITIES_AND_PENDING_EDGES_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report["summary"] if "summary" in report else report,indent=2,ensure_ascii=False,default=str))
print("STATUS =",report["status"])

cur.close()
conn.close()
