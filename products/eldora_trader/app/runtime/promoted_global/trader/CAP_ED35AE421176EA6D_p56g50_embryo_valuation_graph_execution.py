import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G50_EMBRYO_VALUATION_GRAPH_EXECUTION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

plan=json.loads(Path("reports/P5.6G49_OFFSPRING_ENTITY_EXTRACTION/P56G49_OFFSPRING_ENTITY_EXTRACTION_REPORT.json").read_text(encoding="utf-8"))

edges=[
 {"parent":"Blueberry Wine","parent_abbi":"10006167","child":"HC-315","child_abbi":"10025495","relation":"sire","confidence":90},
 {"parent":"Red Wolf","parent_abbi":"10003296","child":"HC-315","child_abbi":"10025495","relation":"sire","confidence":85},
 {"parent":"Perfect Storm","parent_abbi":"10006486","child":"HC-317","child_abbi":"10029805","relation":"sire","confidence":90},
 {"parent":"Moody Blues","parent_abbi":"10025525","child":"HC-317","child_abbi":"10029805","relation":"sire","confidence":85}
]

valuation_ledger={
 "event_type":"embryo_sale",
 "source_url":"https://www.thebreedersconnection.com/lot809.html",
 "lot":"Lot #809",
 "amount":"$3,000.00",
 "unit":"per embryo",
 "quantity_options":"2, 4, or 6 embryos",
 "consignor":"Herrington Cattle Company",
 "buyer":"Gary Long - Washington",
 "status":"LEDGER_ONLY_NO_DB_TABLE_CONFIRMED"
}

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "mode":"DRY_RUN_ROLLBACK_COMMIT_VALIDATE",
 "entities_planned":len(plan["planned_creations"]),
 "edges_planned":len(edges),
 "status":"UNKNOWN",
 "created_entities":[],
 "created_edges":[],
 "skipped":[],
 "valuation_ledger":valuation_ledger
}

try:
    # precheck existing entities
    for e in plan["planned_creations"]:
        cur.execute("select id,official_name from p55a_animals where registry_number=%s",(e["registry_number"],))
        row=cur.fetchone()
        if row:
            report["skipped"].append({"type":"entity","registry_number":e["registry_number"],"reason":"ENTITY_ALREADY_EXISTS"})
        else:
            report["created_entities"].append(e)

    def insert_entities():
        for e in report["created_entities"]:
            cur.execute("""
            insert into p55a_animals
            (id,official_name,registry_number,animal_type,confidence_score,validation_status,notes)
            values (%s,%s,%s,'bull',%s,'provisional','Created from P5.6G50 embryo/valuation extraction.')
            """,(e["id"],e["official_name"],e["registry_number"],e["confidence_score"]))

    # rollback test entities
    cur.execute("BEGIN;")
    insert_entities()
    conn.rollback()

    # commit entities
    insert_entities()
    conn.commit()

    # resolve ids
    cur.execute("select id,official_name,registry_number from p55a_animals")
    animals={r[2]:{"id":str(r[0]),"name":r[1]} for r in cur.fetchall() if r[2]}

    edge_inserts=[]
    for e in edges:
        p=animals.get(e["parent_abbi"])
        c=animals.get(e["child_abbi"])
        if not p or not c:
            report["skipped"].append({**e,"type":"edge","reason":"MISSING_ENTITY"})
            continue
        cur.execute("""
        select id from p55a_pedigree_edges
        where parent_id=%s and child_id=%s and relation=%s
        """,(p["id"],c["id"],e["relation"]))
        if cur.fetchone():
            report["skipped"].append({**e,"type":"edge","reason":"EDGE_ALREADY_EXISTS"})
            continue
        edge_inserts.append({**e,"parent_id":p["id"],"child_id":c["id"]})

    # rollback edges
    cur.execute("BEGIN;")
    for e in edge_inserts:
        cur.execute("""
        insert into p55a_pedigree_edges
        (parent_id,child_id,relation,generation_distance,evidence_source_id,confidence_score,validation_status)
        values (%s,%s,%s,1,null,%s,'provisional')
        """,(e["parent_id"],e["child_id"],e["relation"],e["confidence"]))
    conn.rollback()

    # commit edges
    for e in edge_inserts:
        cur.execute("""
        insert into p55a_pedigree_edges
        (parent_id,child_id,relation,generation_distance,evidence_source_id,confidence_score,validation_status)
        values (%s,%s,%s,1,null,%s,'provisional')
        """,(e["parent_id"],e["child_id"],e["relation"],e["confidence"]))
        report["created_edges"].append(e)
    conn.commit()

    cur.execute("""
    select p.official_name,c.official_name,e.relation,e.confidence_score,e.validation_status
    from p55a_pedigree_edges e
    left join p55a_animals p on p.id=e.parent_id
    left join p55a_animals c on c.id=e.child_id
    where c.registry_number in ('10025495','10029805')
    order by c.official_name,e.confidence_score desc
    """)
    report["validation_edges"]=[list(map(str,r)) for r in cur.fetchall()]

    report["summary"]={
      "entities_created":len(report["created_entities"]),
      "edges_created":len(report["created_edges"]),
      "skipped":len(report["skipped"]),
      "valuation_records_ledged":1
    }
    report["status"]="PASS"

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G50_EMBRYO_VALUATION_GRAPH_EXECUTION_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report.get("summary",report),indent=2,ensure_ascii=False,default=str))
print("STATUS =",report["status"])

cur.close()
conn.close()
