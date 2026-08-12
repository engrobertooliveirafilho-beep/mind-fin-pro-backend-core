import os
import sys
import traceback
from pathlib import Path

def load_env(path=".env"):
    p = Path(path)
    if not p.exists():
        return []
    loaded = []
    for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and v:
            os.environ[k] = v
            loaded.append(k)
    return loaded

def mask(v):
    if not v:
        return "MISSING"
    if len(v) <= 12:
        return "SET_TOO_SHORT"
    return v[:8] + "..." + v[-5:]

def main():
    print("P4.65I_VALIDATE_RETRIEVAL_CONFIG")

    loaded = load_env(".env")
    print("DOTENV_KEYS_LOADED:", loaded)

    openai_key = os.getenv("OPENAI_API_KEY") or ""
    db_url = os.getenv("DATABASE_URL") or ""
    model = os.getenv("NEURA_EMBEDDING_MODEL") or "text-embedding-3-small"

    print("OPENAI_API_KEY:", mask(openai_key), "LEN=", len(openai_key))
    print("NEURA_EMBEDDING_MODEL:", model)
    print("DATABASE_URL:", mask(db_url))

    openai_shape_ok = openai_key.startswith("sk-") and len(openai_key) > 40
    db_shape_ok = db_url.startswith("postgresql://") or db_url.startswith("postgres://")

    print("OPENAI_KEY_SHAPE_OK:", openai_shape_ok)
    print("DATABASE_URL_SHAPE_OK:", db_shape_ok)

    print("\n===== EMBEDDING TEST =====")
    embed_ok = False
    try:
        from app.embedding.provider import EmbeddingProvider
        p = EmbeddingProvider()
        emb = p.embed("P4.65I retrieval config validation")
        embed_ok = bool(emb)
        print("EMBED_OK:", embed_ok)
        print("EMBED_DIM:", len(emb) if emb else 0)
        print("EMBED_ERROR:", getattr(p, "last_error", None))
    except Exception:
        print("EMBED_FATAL")
        print(traceback.format_exc())

    print("\n===== DB TEST =====")
    db_ok = False
    try:
        if not db_shape_ok:
            print("DB_SKIPPED_BAD_SHAPE")
        else:
            import psycopg2
            import psycopg2.extras
            with psycopg2.connect(db_url, connect_timeout=7) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("select 1 as ok")
                    print("DB_CONNECT_OK:", dict(cur.fetchone()))
                    db_ok = True

                    cur.execute("""
                        select exists (
                          select 1 from information_schema.tables
                          where table_name='neura_embeddings'
                        ) as exists
                    """)
                    exists = dict(cur.fetchone())
                    print("NEURA_EMBEDDINGS_TABLE:", exists)

                    if exists.get("exists"):
                        cur.execute("select count(*) as total from neura_embeddings")
                        print("NEURA_EMBEDDINGS_COUNT:", dict(cur.fetchone()))
    except Exception:
        print("DB_FATAL")
        print(traceback.format_exc())

    print("\n===== VERDICT =====")
    if embed_ok and db_ok:
        print("P4.65I_READY_FOR_REAL_RETRIEVAL")
        return 0

    if not openai_shape_ok:
        print("BLOCKED: OPENAI_API_KEY inválida ou ausente.")
    elif not embed_ok:
        print("BLOCKED: OPENAI_API_KEY existe, mas embeddings ainda falham.")

    if not db_shape_ok:
        print("BLOCKED: DATABASE_URL ausente ou formato inválido.")
    elif not db_ok:
        print("BLOCKED: DATABASE_URL existe, mas conexão falhou.")

    print("P4.65I_NOT_READY")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
