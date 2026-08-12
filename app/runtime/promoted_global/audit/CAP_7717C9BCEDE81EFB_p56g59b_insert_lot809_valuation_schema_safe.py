import os,json,uuid,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G59B_INSERT_LOT809_VALUATION_SCHEMA_SAFE"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

LOT809_URL="https://www.thebreedersconnection.com/lot809.html"

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

report={"mission":MISSION,"generated_at":datetime.now(timezone.utc).isoformat(),"status":"UNKNOWN"}

try:
    cur.execute("select id from p55a_sources where source_url=%s limit 1",(LOT809_URL,))
    src=cur.fetchone()
    if not src:
        report["status"]="BLOCKED"
        report["blocker"]="LOT809_SOURCE_NOT_FOUND"
    else:
        source_id=str(src[0])

        cur.execute("select id from p55a_animals where registry_number='10025495' limit 1")
        animal=cur.fetchone()
        animal_id=str(animal[0]) if animal else None

        cur.execute("""
        select id from p55a_valuation_events
        where source_id=%s
          and event_type='embryo_sale'
          and embryo_price=3000.00
        limit 1
        """,(source_id,))
        existing=cur.fetchone()

        if existing:
            report["status"]="PASS_ALREADY_EXISTS"
            report["existing_id"]=str(existing[0])
        else:
            valuation_id=str(uuid.uuid4())
            payload={
              "lot":"Lot #809",
              "amount_text":"$3,000.00 / embryo",
              "quantity_options":"2, 4, or 6 embryos",
              "buyer":"Gary Long - Washington",
              "seller":"Herrington Cattle Company",
              "source_url":LOT809_URL,
              "mission":MISSION
            }

            sql="""
            insert into p55a_valuation_events
            (id, animal_id, event_type, currency, amount, embryo_price,
             buyer, seller, auction_name, source_id, raw_payload,
             confidence_score, validation_status)
            values
            (%s,%s,'embryo_sale','USD',3000.00,3000.00,
             'Gary Long - Washington','Herrington Cattle Company',
             'Breeder''s Connection Lot #809',%s,%s,90,'provisional')
            """

            cur.execute("BEGIN;")
            cur.execute(sql,(valuation_id,animal_id,source_id,json.dumps(payload)))
            cur.execute("select count(*) from p55a_valuation_events where id=%s",(valuation_id,))
            rollback_count=cur.fetchone()[0]
            conn.rollback()

            if rollback_count != 1:
                report["status"]="BLOCKED"
                report["blocker"]="ROLLBACK_TEST_FAILED"
            else:
                cur.execute(sql,(valuation_id,animal_id,source_id,json.dumps(payload)))
                conn.commit()
                report["status"]="PASS"
                report["valuation_id"]=valuation_id

    cur.execute("select count(*) from p55a_valuation_events")
    report["valuation_events_total"]=cur.fetchone()[0]

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G59B_INSERT_LOT809_VALUATION_SCHEMA_SAFE_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report,indent=2,ensure_ascii=False,default=str))

cur.close()
conn.close()
