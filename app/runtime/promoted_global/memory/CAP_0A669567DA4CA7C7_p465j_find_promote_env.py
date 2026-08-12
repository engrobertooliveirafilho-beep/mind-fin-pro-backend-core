import os
import re
from pathlib import Path
import traceback

ROOT = Path(".").resolve()

SECRET_KEYS = [
    "OPENAI_API_KEY",
    "DATABASE_URL",
    "SUPABASE_DB_URL",
    "POSTGRES_URL",
    "POSTGRES_DATABASE_URL",
    "SUPABASE_POSTGRES_URL",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_SERVICE_ROLE",
]

SEARCH_ROOTS = [
    ROOT,
    ROOT / "_evidence",
    ROOT.parent,
]

FILE_NAMES = [
    ".env",
    ".env.local",
    ".env.production",
    ".env.dev",
    ".env.backup",
    "render.yaml",
    "docker-compose.yml",
    "docker-compose.yaml",
    "secrets.txt",
]

def mask(v):
    if not v:
        return "MISSING"
    v = str(v).strip()
    if len(v) <= 12:
        return f"SET_TOO_SHORT(len={len(v)})"
    return f"{v[:8]}...{v[-5:]}(len={len(v)})"

def parse_env_file(path):
    out = {}
    try:
        for raw in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            # KEY=VALUE
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip().strip("-").strip()
                v = v.strip().strip('"').strip("'")
                if k in SECRET_KEYS or any(x in k for x in ["OPENAI", "DATABASE", "POSTGRES", "SUPABASE"]):
                    out[k] = v
    except Exception:
        pass
    return out

print("P4.65J_FIND_PROMOTE_ENV")
print("ROOT:", ROOT)

found = {}

print("\n===== CURRENT PROCESS ENV =====")
for k in SECRET_KEYS:
    v = os.getenv(k)
    print(k, "=", mask(v))
    if v:
        found.setdefault(k, []).append(("process", v))

print("\n===== SEARCH ENV FILES =====")
visited = set()

for root in SEARCH_ROOTS:
    if not root.exists():
        continue

    for path in root.rglob("*"):
        if path in visited:
            continue
        visited.add(path)

        if not path.is_file():
            continue

        if path.name not in FILE_NAMES and not path.name.lower().endswith((".env", ".env.txt")):
            continue

        if any(part in {".venv", "venv", "__pycache__", ".git"} for part in path.parts):
            continue

        vals = parse_env_file(path)
        if vals:
            print("\nFILE:", path)
            for k, v in vals.items():
                print(" ", k, "=", mask(v))
                found.setdefault(k, []).append((str(path), v))

def best_value(*keys):
    for k in keys:
        vals = found.get(k, [])
        for source, v in vals:
            if not v:
                continue
            if k == "OPENAI_API_KEY":
                if v.startswith("sk-") and len(v) > 40:
                    return k, source, v
            elif k in ["DATABASE_URL","SUPABASE_DB_URL","POSTGRES_URL","POSTGRES_DATABASE_URL","SUPABASE_POSTGRES_URL"]:
                if v.startswith("postgres://") or v.startswith("postgresql://"):
                    return k, source, v
            else:
                if len(v) > 20:
                    return k, source, v
    return None, None, None

openai_k, openai_src, openai_val = best_value("OPENAI_API_KEY")
db_k, db_src, db_val = best_value("DATABASE_URL","SUPABASE_DB_URL","POSTGRES_URL","POSTGRES_DATABASE_URL","SUPABASE_POSTGRES_URL")

print("\n===== BEST CANDIDATES =====")
print("OPENAI:", openai_k, openai_src, mask(openai_val))
print("DATABASE:", db_k, db_src, mask(db_val))

# promote into current process for immediate validation
if openai_val:
    os.environ["OPENAI_API_KEY"] = openai_val
if db_val:
    os.environ["DATABASE_URL"] = db_val

print("\n===== PROMOTED CURRENT PROCESS =====")
print("OPENAI_API_KEY =", mask(os.getenv("OPENAI_API_KEY")))
print("DATABASE_URL =", mask(os.getenv("DATABASE_URL")))

print("\n===== VALIDATION =====")

embed_ok = False
db_ok = False

try:
    from app.embedding.provider import EmbeddingProvider
    p = EmbeddingProvider()
    emb = p.embed("P4.65J validate existing MIND openai key")
    embed_ok = bool(emb)
    print("EMBED_OK:", embed_ok)
    print("EMBED_DIM:", len(emb) if emb else 0)
    print("EMBED_ERROR:", getattr(p, "last_error", None))
except Exception:
    print("EMBED_FATAL")
    print(traceback.format_exc())

try:
    db = os.getenv("DATABASE_URL")
    if not db:
        print("DB_MISSING")
    else:
        import psycopg2, psycopg2.extras
        with psycopg2.connect(db, connect_timeout=7) as conn:
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

print("\n===== WRITE PROMOTION PATCH? =====")
env_path = ROOT / ".env"
if openai_val or db_val:
    current = env_path.read_text(encoding="utf-8", errors="ignore") if env_path.exists() else ""

    additions = []
    if openai_val and "OPENAI_API_KEY=" not in current:
        additions.append("OPENAI_API_KEY=" + openai_val)
    if db_val and "DATABASE_URL=" not in current:
        additions.append("DATABASE_URL=" + db_val)
    if "NEURA_EMBEDDING_MODEL=" not in current:
        additions.append("NEURA_EMBEDDING_MODEL=text-embedding-3-small")

    if additions:
        backup = ROOT / f"_evidence/P4_65J_env_backup_{os.getpid()}.env"
        backup.parent.mkdir(parents=True, exist_ok=True)
        if env_path.exists():
            backup.write_text(current, encoding="utf-8")

        with env_path.open("a", encoding="utf-8") as f:
            f.write("\n\n# P4.65J promoted retrieval config\n")
            for line in additions:
                f.write(line + "\n")

        print("ENV_PATCH_APPLIED:", [x.split('=')[0] for x in additions])
    else:
        print("ENV_PATCH_NOT_NEEDED")
else:
    print("NO_VALID_CANDIDATES_FOUND")

print("\n===== VERDICT =====")
if embed_ok and db_ok:
    print("P4.65J_READY_FOR_REAL_RETRIEVAL")
else:
    print("P4.65J_NOT_READY")
    if not embed_ok:
        print("BLOCKED_OPENAI")
    if not db_ok:
        print("BLOCKED_DATABASE")

print("P4.65J_COMPLETE")
