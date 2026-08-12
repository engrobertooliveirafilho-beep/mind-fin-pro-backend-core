import os, json, uuid, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G37E_PARENT_EXPANSION_EXECUTION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

SOURCE_21_URL="http://members.americanbuckingbull.com/bulls.aspx?id=21"
SOURCE_REINDEER_URL="http://members.americanbuckingbull.com/bulls.aspx?id=10010628"
SOURCE_MO110_URL="http://members.americanbuckingbull.com/bulls.aspx?id=10007793"

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "phases":{},
 "status":"UNKNOWN"
}

try:
    # Resolve existing
    cur.execute("select id from p55a_animals where registry_number='10010628'")
    reindeer_id=cur.fetchone()[0]

    cur.execute("select id from p55a_animals where registry_number='10007793'")
    mo110_id=cur.fetchone()[0]

    # Precheck duplicates
    regs=["21","10000789","10006436","10002937","39"]
    cur.execute("select registry_number,count(*) from p55a_animals where registry_number=any(%s) group by registry_number", (regs,))
    existing={r[0]:r[1] for r in cur.fetchall()}

    if existing:
        report["status"]="BLOCKED"
        report["blocker"]="One or more target registry_numbers already exist"
        report["existing"]=existing
    else:
        ids={
          "naccarato_id":str(uuid.uuid4()),
          "diamond_id":str(uuid.uuid4()),
          "oscar_velvet_id":str(uuid.uuid4()),
          "jr34_id":str(uuid.uuid4()),
          "ratjen_id":str(uuid.uuid4()),
          "edge_naccarato_reindeer":str(uuid.uuid4()),
          "edge_diamond_mo110":str(uuid.uuid4())
        }

        report["phases"]["dry_run"]={
          "reindeer_id":str(reindeer_id),
          "mo110_id":str(mo110_id),
          "new_ids":ids
        }

        sql=f"""
        -- name reconciliation
        update p55a_animals
        set official_name='REINDEER',
            aliases=array_append(aliases,'REINDEER MO'),
            updated_at=now()
        where id='{reindeer_id}';

        update p55a_animals
        set official_name='MO 110',
            aliases=array_append(aliases,'110'),
            updated_at=now()
        where id='{mo110_id}';

        -- generation 2 entities
        insert into p55a_animals
        (id, official_name, registry_number, animal_type, confidence_score, validation_status, notes)
        values
        ('{ids["naccarato_id"]}','NACCARATO BREEDING','21','bull',85,'provisional','ABBI#21 parsed from official ABBI profile.'),
        ('{ids["diamond_id"]}','DIAMOND''S GHOST','10000789','bull',85,'provisional','ABBI sire of MO 110 from ABBI#10007793.'),
        ('{ids["oscar_velvet_id"]}','NACCARATO''S OSCARS VELVET','10006436','bull',80,'provisional','Grandparent candidate from ABBI#10010628.'),
        ('{ids["jr34_id"]}','JR 34','10002937','bull',80,'provisional','Grandparent candidate from ABBI#10007793.'),
        ('{ids["ratjen_id"]}','RATJEN BREEDING','39','bull',80,'provisional','Grandparent candidate from ABBI#10007793.');

        -- generation 2 edges
        insert into p55a_pedigree_edges
        (id,parent_id,child_id,relation,generation_distance,evidence_source_id,confidence_score,validation_status)
        values
        ('{ids["edge_naccarato_reindeer"]}','{ids["naccarato_id"]}','{reindeer_id}','sire',1,null,85,'provisional'),
        ('{ids["edge_diamond_mo110"]}','{ids["diamond_id"]}','{mo110_id}','sire',1,null,85,'provisional');
        """

        # rollback test
        cur.execute("BEGIN;")
        cur.execute(sql)
        cur.execute("select count(*) from p55a_animals where registry_number=any(%s)", (regs,))
        rollback_count=cur.fetchone()[0]
        conn.rollback()

        report["phases"]["rollback_test"]={
          "inserted_entities_inside_rollback":rollback_count,
          "status":"PASS" if rollback_count==5 else "REVIEW_REQUIRED"
        }

        if rollback_count != 5:
            report["status"]="BLOCKED"
            report["blocker"]="Rollback test did not produce expected entity count"
        else:
            # commit
            cur.execute(sql)
            conn.commit()
            report["phases"]["commit"]="COMMIT_EXECUTED"

            # validate
            cur.execute("""
            select official_name, registry_number, aliases, confidence_score, validation_status
            from p55a_animals
            where registry_number=any(%s)
            order by registry_number
            """,(regs+["10010628","10007793"],))
            animals=cur.fetchall()

            cur.execute("""
            select p.official_name,c.official_name,e.relation,e.confidence_score,e.validation_status
            from p55a_pedigree_edges e
            left join p55a_animals p on p.id=e.parent_id
            left join p55a_animals c on c.id=e.child_id
            where c.registry_number in ('10010628','10007793')
            order by c.official_name,e.relation
            """)
            edges=cur.fetchall()

            report["phases"]["validate"]={
              "animals":[list(map(str,r)) for r in animals],
              "edges":[list(map(str,r)) for r in edges]
            }

            report["status"]="PASS"

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G37E_PARENT_EXPANSION_EXECUTION_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report,indent=2,ensure_ascii=False,default=str))

cur.close()
conn.close()
