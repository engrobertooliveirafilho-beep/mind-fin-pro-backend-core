import os
import sys
import traceback
import importlib.metadata

print("P4.65F_PROVIDER_DB_AUDIT")

def mask(v):
    if not v:
        return "MISSING"
    s = str(v)
    if len(s) <= 10:
        return "SET_SHORT"
    return s[:6] + "..." + s[-4:]

print("\n===== PYTHON / SDK =====")
print("python:", sys.version)
for pkg in ["openai", "psycopg2", "psycopg2-binary"]:
    try:
        print(pkg, importlib.metadata.version(pkg))
    except Exception:
        print(pkg, "NOT_FOUND")

print("\n===== ENV SAFE =====")
for k in [
    "OPENAI_API_KEY",
    "OPENAI_EMBEDDING_MODEL",
    "EMBEDDING_MODEL",
    "DATABASE_URL",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE",
    "SUPABASE_SERVICE_ROLE_KEY",
]:
    print(k, "=", mask(os.getenv(k)))

print("\n===== DOTENV FILES =====")
for name in [".env", ".env.local", ".env.production", ".env.dev"]:
    if os.path.exists(name):
        print("FOUND", name)
        with open(name, "r", encoding="utf-8", errors="ignore") as f:
            for line in f.readlines():
                if any(x in line for x in ["DATABASE_URL", "OPENAI", "EMBEDDING", "SUPABASE"]):
                    key = line.split("=", 1)[0].strip()
                    val = line.split("=", 1)[1].strip() if "=" in line else ""
                    print(name, key, "=", mask(val))
    else:
        print("MISSING", name)

print("\n===== PROVIDER OBJECT =====")
try:
    from app.embedding.provider import EmbeddingProvider
    p = EmbeddingProvider()
    print("provider_class:", type(p).__name__)
    print("provider_model:", getattr(p, "model", None))
    print("provider_attrs:", {k: str(v)[:120] for k, v in vars(p).items() if "key" not in k.lower()})
except Exception:
    print("PROVIDER_OBJECT_ERROR")
    print(traceback.format_exc())

print("\n===== OPENAI EMBEDDING MINIMAL TEST =====")
try:
    from openai import OpenAI
    client = OpenAI()
    models_to_test = []
    env_model = os.getenv("OPENAI_EMBEDDING_MODEL") or os.getenv("EMBEDDING_MODEL")
    if env_model:
        models_to_test.append(env_model)
    try:
        from app.embedding.provider import EmbeddingProvider
        models_to_test.append(getattr(EmbeddingProvider(), "model", ""))
    except Exception:
        pass
    models_to_test += ["text-embedding-3-small", "text-embedding-3-large"]
    seen = []
    for m in models_to_test:
        if not m or m in seen:
            continue
        seen.append(m)
        print("\nTEST_MODEL:", m)
        try:
            r = client.embeddings.create(model=m, input="test")
            emb = r.data[0].embedding
            print("OK", m, "DIM", len(emb))
        except Exception as e:
            print("FAIL", m)
            print(type(e).__name__, str(e)[:1200])
except Exception:
    print("OPENAI_TEST_FATAL")
    print(traceback.format_exc())

print("\n===== DATABASE_URL CONNECTION TEST =====")
try:
    db = os.getenv("DATABASE_URL")
    if not db:
        print("DATABASE_URL_MISSING")
    else:
        import psycopg2
        import psycopg2.extras
        with psycopg2.connect(db, connect_timeout=5) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select 1 as ok")
                print("DB_CONNECT_OK", dict(cur.fetchone()))
                cur.execute("""
                    select exists (
                        select 1 from information_schema.tables
                        where table_name='neura_embeddings'
                    ) as exists
                """)
                print("NEURA_EMBEDDINGS_EXISTS", dict(cur.fetchone()))
except Exception:
    print("DB_CONNECT_ERROR")
    print(traceback.format_exc())

print("\nP4.65F_PROVIDER_DB_AUDIT_COMPLETE")
