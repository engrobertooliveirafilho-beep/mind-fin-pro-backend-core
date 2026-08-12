import os
import re
import sys
import traceback
from pathlib import Path

print("P4.65H_ENV_EMBED_DB_AUDIT")

def mask(v):
    if not v:
        return "MISSING"
    v = str(v).strip()
    if len(v) <= 12:
        return "SET_SHORT"
    return v[:8] + "..." + v[-5:]

def load_dotenv_manual(path=".env"):
    p = Path(path)
    loaded = []
    if not p.exists():
        print("DOTENV_MISSING", path)
        return loaded

    for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v
            loaded.append(k)
    print("DOTENV_LOADED_KEYS:", loaded)
    return loaded

print("\n===== BEFORE LOAD =====")
for k in ["OPENAI_API_KEY","NEURA_EMBEDDING_MODEL","DATABASE_URL","SUPABASE_URL","SUPABASE_DB_URL","SUPABASE_SERVICE_ROLE_KEY"]:
    print(k, "=", mask(os.getenv(k)))

load_dotenv_manual(".env")

# common aliases
if not os.getenv("DATABASE_URL"):
    for alias in ["SUPABASE_DB_URL", "POSTGRES_URL", "POSTGRES_DATABASE_URL", "SUPABASE_POSTGRES_URL"]:
        if os.getenv(alias):
            os.environ["DATABASE_URL"] = os.getenv(alias)
            print("DATABASE_URL_SET_FROM_ALIAS:", alias)
            break

print("\n===== AFTER LOAD =====")
for k in ["OPENAI_API_KEY","NEURA_EMBEDDING_MODEL","DATABASE_URL","SUPABASE_URL","SUPABASE_DB_URL","SUPABASE_SERVICE_ROLE_KEY"]:
    print(k, "=", mask(os.getenv(k)))

print("\n===== OPENAI KEY SHAPE =====")
key = os.getenv("OPENAI_API_KEY") or ""
print("KEY_LEN:", len(key))
print("KEY_PREFIX:", key[:12] if key else "MISSING")
print("LOOKS_PROJECT_KEY:", key.startswith("sk-proj-"))
print("LOOKS_LEGACY_KEY:", key.startswith("sk-"))

print("\n===== EMBEDDING REAL TEST =====")
try:
    from app.embedding.provider import EmbeddingProvider
    p = EmbeddingProvider()
    emb = p.embed("P4.65H embedding validation")
    print("MODEL:", p.model)
    print("EMBED_OK:", bool(emb))
    print("EMBED_DIM:", len(emb) if emb else 0)
    print("EMBED_ERROR:", p.last_error)
except Exception:
    print("EMBED_FATAL")
    print(traceback.format_exc())

print("\n===== DATABASE_URL REAL TEST =====")
try:
    db = os.getenv("DATABASE_URL")
    if not db:
        print("DB_MISSING")
    else:
        import psycopg2
        import psycopg2.extras
        with psycopg2.connect(db, connect_timeout=5) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select 1 as ok")
                print("DB_CONNECT_OK:", dict(cur.fetchone()))
                cur.execute("""
                    select exists (
                      select 1 from information_schema.tables
                      where table_name='neura_embeddings'
                    ) as exists
                """)
                print("NEURA_EMBEDDINGS_TABLE:", dict(cur.fetchone()))
                cur.execute("select count(*) as total from neura_embeddings")
                print("NEURA_EMBEDDINGS_COUNT:", dict(cur.fetchone()))
except Exception:
    print("DB_FATAL")
    print(traceback.format_exc())

print("\n===== SEMANTIC PROVIDER STATUS =====")
try:
    from app.retrieval.semantic_provider import SemanticRetrievalProvider
    sp = SemanticRetrievalProvider()
    rows = sp.search("p465h_user", "Eldora MIND Drive knowledge graph", limit=3)
    print("ROWS:", len(rows))
    print("STATUS:", sp.status())
    for r in rows:
        print("ROW:", str(r.get("score")), str(r.get("sender_id")), str(r.get("message"))[:300])
except Exception:
    print("SEMANTIC_PROVIDER_FATAL")
    print(traceback.format_exc())

print("\n===== VERDICT =====")
embed_ok = False
db_ok = False

try:
    from app.embedding.provider import EmbeddingProvider
    pp = EmbeddingProvider()
    embed_ok = bool(pp.embed("verdict"))
except Exception:
    embed_ok = False

db_ok = bool(os.getenv("DATABASE_URL"))

if embed_ok and db_ok:
    print("P4.65H_READY_FOR_REAL_RETRIEVAL")
elif not embed_ok and not db_ok:
    print("P4.65H_BLOCKED_OPENAI_KEY_AND_DATABASE_URL")
elif not embed_ok:
    print("P4.65H_BLOCKED_OPENAI_KEY")
elif not db_ok:
    print("P4.65H_BLOCKED_DATABASE_URL")

print("P4.65H_COMPLETE")
