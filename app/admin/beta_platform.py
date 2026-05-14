import os, psycopg2, psycopg2.extras, time
from fastapi import APIRouter, Header, HTTPException

router = APIRouter()

def admin_guard(token):
    if token != os.getenv("ADMIN_ACTIVATION_TOKEN"):
        raise HTTPException(status_code=403, detail="forbidden")

def db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@router.post("/admin/beta/platform/activate")
def activate_beta_platform(x_admin_token: str = Header(default="")):
    admin_guard(x_admin_token)
    t0=time.time()
    with db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            create table if not exists beta_users(
              phone text primary key,
              name text,
              tier text default 'FREE',
              enabled boolean default true,
              created_at timestamptz default now()
            );
            create table if not exists user_feedback_log(
              id bigserial primary key,
              sender_id text,
              rating int,
              feedback text,
              created_at timestamptz default now()
            );
            create table if not exists runtime_metrics(
              id bigserial primary key,
              sender_id text,
              route text,
              latency_ms int,
              semantic_hit boolean,
              memory_recall boolean,
              tokens int default 0,
              created_at timestamptz default now()
            );
            create table if not exists memory_quality_metrics(
              id bigserial primary key,
              sender_id text,
              context_depth int default 0,
              recall_precision numeric default 0,
              semantic_continuity numeric default 0,
              created_at timestamptz default now()
            );
            create table if not exists plan_configuration(
              plan text primary key,
              max_messages_day int,
              memory_depth int,
              semantic_enabled boolean,
              premium boolean,
              created_at timestamptz default now()
            );
            insert into plan_configuration(plan,max_messages_day,memory_depth,semantic_enabled,premium)
            values
            ('FREE',30,3,true,false),
            ('PREMIUM',500,20,true,true),
            ('BUSINESS',5000,50,true,true)
            on conflict(plan) do update set
              max_messages_day=excluded.max_messages_day,
              memory_depth=excluded.memory_depth,
              semantic_enabled=excluded.semantic_enabled,
              premium=excluded.premium;
            create table if not exists usage_tracking(
              id bigserial primary key,
              sender_id text,
              plan text default 'FREE',
              messages_count int default 0,
              embedding_calls int default 0,
              retrieval_calls int default 0,
              estimated_cost numeric default 0,
              period date default current_date,
              created_at timestamptz default now()
            );
            create table if not exists premium_feature_flags(
              flag text primary key,
              enabled boolean default false,
              plans text[],
              created_at timestamptz default now()
            );
            insert into premium_feature_flags(flag,enabled,plans)
            values
            ('deep_memory',true,array['PREMIUM','BUSINESS']),
            ('long_context',true,array['PREMIUM','BUSINESS']),
            ('priority_semantic_retrieval',true,array['BUSINESS']),
            ('advanced_reports',false,array['BUSINESS'])
            on conflict(flag) do update set enabled=excluded.enabled, plans=excluded.plans;
            """)
            conn.commit()

            cur.execute("select count(*) c from beta_users")
            beta_count=cur.fetchone()["c"]
            cur.execute("select count(*) c from plan_configuration")
            plans_count=cur.fetchone()["c"]
            cur.execute("select count(*) c from premium_feature_flags")
            flags_count=cur.fetchone()["c"]

    return {
      "status":"NEURA_REAL_BETA_PLATFORM_OPERATIONAL",
      "beta_users_table": True,
      "feedback_log": True,
      "runtime_metrics": True,
      "memory_quality_metrics": True,
      "billing_readiness": True,
      "plans_count": plans_count,
      "premium_flags_count": flags_count,
      "beta_users_count": beta_count,
      "latency_ms": int((time.time()-t0)*1000)
    }
