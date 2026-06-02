
import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone

def _db():
    return os.getenv("DATABASE_URL")

def ensure_friendship_profile(sender_id: str, name: str = "Roberto") -> dict:
    if not _db():
        return {"ok": False, "error": "DATABASE_URL_MISSING"}
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            insert into neura_friendship_profile(sender_id,name,relationship_stage,proactive_sent_today,daily_limit)
            values (%s,%s,%s,0,1)
            on conflict(sender_id) do update set
              name=coalesce(neura_friendship_profile.name, excluded.name),
              relationship_stage=coalesce(neura_friendship_profile.relationship_stage, excluded.relationship_stage),
              updated_at=now()
            returning *
            """,(sender_id,name,"active"))
            profile=dict(cur.fetchone())

            cur.execute("""
            insert into neura_user_preferences(sender_id,opt_out,preferred_time_window,tone)
            values (%s,false,'morning','natural_light_useful')
            on conflict(sender_id) do nothing
            returning *
            """,(sender_id,))
            pref=cur.fetchone()

            if not pref:
                cur.execute("select * from neura_user_preferences where sender_id=%s",(sender_id,))
                pref=cur.fetchone()

        conn.commit()
    return {"ok": True, "profile": profile, "preferences": dict(pref)}

def plan_proactive_checkin(sender_id: str, message: str, reason: str = "semantic_context") -> dict:
    if not _db():
        return {"ok": False, "error": "DATABASE_URL_MISSING"}

    ensure_friendship_profile(sender_id)

    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("select opt_out, preferred_time_window, tone from neura_user_preferences where sender_id=%s",(sender_id,))
            prefs=dict(cur.fetchone() or {})
            if prefs.get("opt_out"):
                return {"ok": False, "blocked": True, "reason": "opt_out"}

            cur.execute("select proactive_sent_today,daily_limit from neura_friendship_profile where sender_id=%s",(sender_id,))
            profile=dict(cur.fetchone() or {})
            if int(profile.get("proactive_sent_today") or 0) >= int(profile.get("daily_limit") or 1):
                return {"ok": False, "blocked": True, "reason": "daily_limit"}

            cur.execute("""
            insert into neura_proactive_messages(sender_id,message,reason,status)
            values (%s,%s,%s,'planned')
            returning id,sender_id,message,reason,status,created_at
            """,(sender_id,message,reason))
            row=dict(cur.fetchone())

        conn.commit()

    return {"ok": True, "planned": row, "preferences": prefs}

def build_contextual_checkin(sender_id: str) -> str:
    try:
        from app.eldora.core.semantic_memory_engine import semantic_memory_recall
        data=semantic_memory_recall(sender_id,"estudo prova matemática objetivo treino projeto",3)
        memories=[str(x.get("message","")) for x in data.get("results",[]) if x.get("message")]
        joined=" ".join(memories).lower()
        if "matemática" in joined or "matematica" in joined:
            return "Roberto, quer que eu monte uma revisão rápida de matemática de 10 minutos hoje?"
        if "projeto" in joined or "eldora" in joined:
            return "Roberto, quer que eu organize o próximo passo da Eldora agora?"
    except Exception:
        pass
    return "Roberto, quer que eu organize seu próximo passo agora?"

def friendship_runtime_status(sender_id: str) -> dict:
    if not _db():
        return {"ok": False, "error": "DATABASE_URL_MISSING"}
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("select * from neura_friendship_profile where sender_id=%s",(sender_id,))
            profile=cur.fetchone()
            cur.execute("select * from neura_user_preferences where sender_id=%s",(sender_id,))
            prefs=cur.fetchone()
            cur.execute("select id,message,reason,status,created_at from neura_proactive_messages where sender_id=%s order by created_at desc limit 5",(sender_id,))
            messages=[dict(x) for x in cur.fetchall()]
    return {"ok": True, "profile": dict(profile) if profile else None, "preferences": dict(prefs) if prefs else None, "recent": messages}
