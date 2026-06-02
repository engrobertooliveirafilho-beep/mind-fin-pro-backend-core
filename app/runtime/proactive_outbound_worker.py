
import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone

def _db():
    return os.getenv("DATABASE_URL")

def _twilio_ready():
    return bool(os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN") and os.getenv("TWILIO_WHATSAPP_FROM"))

def _send_twilio_whatsapp(to: str, body: str) -> dict:
    if not _twilio_ready():
        return {"ok": False, "error": "TWILIO_ENV_MISSING"}

    try:
        from twilio.rest import Client
        client=Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        msg=client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            to=to,
            body=body
        )
        return {"ok": True, "sid": msg.sid, "status": msg.status}
    except Exception as e:
        return {"ok": False, "error": str(e)[:500]}

def fetch_next_planned(sender_id: str | None = None) -> dict | None:
    if not _db():
        return None

    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if sender_id:
                cur.execute("""
                select p.id,p.sender_id,p.message,p.reason,p.status,p.created_at,
                       coalesce(u.opt_out,false) as opt_out,
                       coalesce(f.proactive_sent_today,0) as proactive_sent_today,
                       coalesce(f.daily_limit,1) as daily_limit
                from neura_proactive_messages p
                left join neura_user_preferences u on u.sender_id=p.sender_id
                left join neura_friendship_profile f on f.sender_id=p.sender_id
                where p.status='planned' and p.sender_id=%s
                order by p.created_at asc
                limit 1
                """,(sender_id,))
            else:
                cur.execute("""
                select p.id,p.sender_id,p.message,p.reason,p.status,p.created_at,
                       coalesce(u.opt_out,false) as opt_out,
                       coalesce(f.proactive_sent_today,0) as proactive_sent_today,
                       coalesce(f.daily_limit,1) as daily_limit
                from neura_proactive_messages p
                left join neura_user_preferences u on u.sender_id=p.sender_id
                left join neura_friendship_profile f on f.sender_id=p.sender_id
                where p.status='planned'
                order by p.created_at asc
                limit 1
                """)
            row=cur.fetchone()
            return dict(row) if row else None

def mark_message(message_id: int, status: str, detail: str = "") -> dict:
    if not _db():
        return {"ok": False, "error": "DATABASE_URL_MISSING"}

    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            update neura_proactive_messages
            set status=%s
            where id=%s
            returning id,sender_id,message,reason,status,created_at
            """,(status,message_id))
            row=dict(cur.fetchone())
        conn.commit()

    return {"ok": True, "message": row, "detail": detail}

def run_proactive_outbound_once(sender_id: str | None = None, dry_run: bool = True) -> dict:
    item=fetch_next_planned(sender_id)
    if not item:
        return {"ok": True, "action": "none", "reason": "no_planned_message"}

    if item.get("opt_out"):
        return mark_message(item["id"], "blocked_opt_out", "user opted out")

    if int(item.get("proactive_sent_today") or 0) >= int(item.get("daily_limit") or 1):
        return mark_message(item["id"], "blocked_daily_limit", "daily limit reached")

    if dry_run:
        return {"ok": True, "action": "dry_run", "candidate": item}

    sent=_send_twilio_whatsapp(item["sender_id"], item["message"])
    if not sent.get("ok"):
        return mark_message(item["id"], "send_failed", sent.get("error","unknown"))

    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor() as cur:
            cur.execute("""
            update neura_proactive_messages set status='sent' where id=%s
            """,(item["id"],))
            cur.execute("""
            update neura_friendship_profile
            set proactive_sent_today=coalesce(proactive_sent_today,0)+1,
                last_proactive_sent_at=now(),
                updated_at=now()
            where sender_id=%s
            """,(item["sender_id"],))
        conn.commit()

    return {"ok": True, "action": "sent", "message_id": item["id"], "twilio": sent}
