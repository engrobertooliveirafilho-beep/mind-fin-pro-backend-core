import os,json,uuid,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G59_VALUATION_TABLE_SCHEMA_AND_INSERTION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

LOT809_URL="https://www.thebreedersconnection.com/lot809.html"

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "mode":"SCHEMA_CHECK_CREATE_ROLLBACK_COMMIT_VALIDATE",
 "status":"UNKNOWN"
}

try:
    # schema check
    cur.execute("""
    select exists (
      select 1 from information_schema.tables
      where table_name='p55a_valuation_events'
    )
    """)
    table_exists=cur.fetchone()[0]
    report["table_existed_before"]=table_exists

    create_sql="""
    create table if not exists p55a_valuation_events (
      id uuid primary key,
      animal_id uuid null,
      source_id uuid not null,
      event_type text not null,
      valuation_type text null,
      amount numeric null,
      currency text null,
      quantity numeric null,
      unit text null,
      seller text null,
      buyer text null,
      event_date date null,
      confidence_score numeric null,
      validation_status text not null default 'provisional',
      raw_payload jsonb null,
      created_at timestamptz not null default now()
    )
    """

    # create table
    cur.execute(create_sql)
    conn.commit()

    # resolve source
    cur.execute("""
    select id from p55a_sources
    where source_url=%s
    order by confidence_score desc nulls last
    limit 1
    """,(LOT809_URL,))
    src=cur.fetchone()

    if not src:
        report["status"]="BLOCKED"
        report["blocker"]="LOT809_SOURCE_NOT_FOUND"
    else:
        source_id=str(src[0])

        # optional linked animal: HC-315 as first embryo dam record
        cur.execute("""
        select id from p55a_animals
        where registry_number='10025495'
        limit 1
        """)
        animal=cur.fetchone()
        animal_id=str(animal[0]) if animal else None

        valuation_id=str(uuid.uuid4())

        payload={
          "lot":"Lot #809",
          "source_url":LOT809_URL,
          "amount_text":"$3,000.00 / embryo",
          "quantity_options":"2, 4, or 6 embryos",
          "consignor":"Herrington Cattle Company",
          "buyer":"Gary Long - Washington",
          "linked_animals":[
            "Blueberry Wine",
            "HC-315",
            "Red Wolf",
            "Perfect Storm",
            "HC-317",
            "Moody Blues"
          ],
          "mission":"P5.6G59"
        }

        insert_sql="""
        insert into p55a_valuation_events
        (id, animal_id, source_id, event_type, valuation_type, amount, currency,
         quantity, unit, seller, buyer, event_date, confidence_score,
         validation_status, raw_payload)
        values
        (%s,%s,%s,'embryo_sale','embryo_price',3000.00,'USD',
         null,'per embryo','Herrington Cattle Company','Gary Long - Washington',
         null,90,'provisional',%s)
        """

        # duplicate check
        cur.execute("""
        select id from p55a_valuation_events
        where source_id=%s
          and event_type='embryo_sale'
          and valuation_type='embryo_price'
          and amount=3000.00
        limit 1
        """,(source_id,))
        existing=cur.fetchone()

        if existing:
            report["status"]="PASS_ALREADY_EXISTS"
            report["existing_valuation_id"]=str(existing[0])
        else:
            # rollback test
            cur.execute("BEGIN;")
            cur.execute(insert_sql,(valuation_id,animal_id,source_id,json.dumps(payload)))
            cur.execute("select count(*) from p55a_valuation_events where id=%s",(valuation_id,))
            rollback_count=cur.fetchone()[0]
            conn.rollback()

            if rollback_count != 1:
                report["status"]="BLOCKED"
                report["blocker"]="ROLLBACK_TEST_FAILED"
            else:
                cur.execute(insert_sql,(valuation_id,animal_id,source_id,json.dumps(payload)))
                conn.commit()

                cur.execute("""
                select id,event_type,valuation_type,amount,currency,unit,seller,buyer,validation_status
                from p55a_valuation_events
                where id=%s
                """,(valuation_id,))
                row=cur.fetchone()

                report["valuation_inserted"]={
                  "id":str(row[0]),
                  "event_type":row[1],
                  "valuation_type":row[2],
                  "amount":str(row[3]),
                  "currency":row[4],
                  "unit":row[5],
                  "seller":row[6],
                  "buyer":row[7],
                  "validation_status":row[8]
                }
                report["status"]="PASS"

    cur.execute("select count(*) from p55a_valuation_events")
    report["valuation_events_total"]=cur.fetchone()[0]

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G59_VALUATION_TABLE_SCHEMA_AND_INSERTION_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report,indent=2,ensure_ascii=False,default=str))

cur.close()
conn.close()
