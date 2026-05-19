
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from fastapi import APIRouter
import os, psycopg2
from twilio.rest import Client

router = APIRouter(prefix="/admin/friendship", tags=["friendship-admin"])

@router.post("/outbound/test")
async def friendship_outbound_test(payload: dict):
    db=os.getenv("DATABASE_URL")
    sid=os.getenv("TWILIO_ACCOUNT_SID")
    token=os.getenv("TWILIO_AUTH_TOKEN")
    from_number=os.getenv("TWILIO_WHATSAPP_FROM") or "whatsapp:+14155238886"

    to=payload.get("to")
    name=payload.get("name","Roberto")
    message=payload.get("message") or f"Bom dia, {name}. Quer revisar matemática por 10 min comigo hoje?"

    if not db:
        return {"sent":False,"reason":"DATABASE_URL_MISSING"}
    if not sid or not token:
        return {"sent":False,"reason":"TWILIO_ENV_MISSING"}
    if not to:
        return {"sent":False,"reason":"TO_MISSING"}

    with psycopg2.connect(db, sslmode="require") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT opt_out FROM neura_user_preferences WHERE sender_id=%s", (to,))
            row=cur.fetchone()
            if row and row[0] is True:
                return {"sent":False,"reason":"OPT_OUT"}

            cur.execute("""
              INSERT INTO neura_proactive_messages(sender_id,message,reason,status)
              VALUES (%s,%s,%s,%s) RETURNING id
            """, (to,message,"outbound_test","planned"))
            msg_id=cur.fetchone()[0]

    client=Client(sid, token)
    twilio_msg=client.messages.create(from_=from_number, to=to, body=message)

    with psycopg2.connect(db, sslmode="require") as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE neura_proactive_messages SET status=%s WHERE id=%s", ("sent", msg_id))

    return {"sent":True,"reason":"OK","twilio_sid":twilio_msg.sid,"message_id":msg_id,"to":to}


# FINAL_IDENTITY_BLOCK
def __identity_guard_last_hop(answer,user_message=""):
    return enforce_no_identity_in_normal_chat(user_message,answer)
