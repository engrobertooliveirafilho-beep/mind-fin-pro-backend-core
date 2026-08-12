import os
import json
import urllib.request
import urllib.parse
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
    v = str(v)
    if len(v) <= 12:
        return f"SET_SHORT(len={len(v)})"
    return f"{v[:8]}...{v[-5:]}(len={len(v)})"

load_env(".env")

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE") or ""

print("P4.65K_SUPABASE_REST_DISCOVERY")
print("SUPABASE_URL:", mask(SUPABASE_URL))
print("SUPABASE_KEY:", mask(SUPABASE_KEY))

if not SUPABASE_URL or not SUPABASE_KEY:
    print("BLOCKED_SUPABASE_REST_CREDENTIALS_MISSING")
    raise SystemExit(0)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def get(path):
    url = SUPABASE_URL + path
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        raw = urllib.request.urlopen(req, timeout=12).read().decode("utf-8")
        return True, json.loads(raw)
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:500]}"

tables_to_probe = [
    "neura_embeddings",
    "neura_memory",
    "mind_config",
    "app_config",
    "runtime_config",
    "secrets",
    "eldora_config",
    "documents",
    "chunks",
    "knowledge_base",
    "mind_knowledge_base",
    "drive_documents",
    "drive_chunks",
]

print("\n===== TABLE PROBE =====")

for table in tables_to_probe:
    ok, data = get(f"/rest/v1/{table}?select=*&limit=1")
    if ok:
        count = len(data) if isinstance(data, list) else "?"
        print(f"TABLE_OK {table} rows_sample={count}")
        if isinstance(data, list) and data:
            row = data[0]
            safe_keys = list(row.keys())
            print("  keys:", safe_keys)
            for k, v in row.items():
                sv = str(v)
                if any(x in k.lower() for x in ["key","secret","token","password","url"]):
                    print(" ", k, "=", mask(sv))
                else:
                    print(" ", k, "=", sv[:180])
    else:
        print(f"TABLE_NO {table} -> {data}")

print("\n===== SEARCH CONFIG-LIKE VALUES IN ACCESSIBLE TABLES =====")

for table in tables_to_probe:
    ok, data = get(f"/rest/v1/{table}?select=*&limit=20")
    if not ok or not isinstance(data, list):
        continue
    hits = []
    for row in data:
        for k, v in row.items():
            sv = str(v)
            if any(token in sv for token in ["postgres://", "postgresql://", "sk-", "OPENAI_API_KEY", "DATABASE_URL"]):
                hits.append((k, sv))
    if hits:
        print("CONFIG_HITS_TABLE:", table)
        for k, v in hits:
            print(" ", k, "=", mask(v))

print("\n===== NEURA_EMBEDDINGS REST COUNT SAMPLE =====")
ok, data = get("/rest/v1/neura_embeddings?select=sender_id,message,metadata&limit=5")
if ok:
    print("NEURA_EMBEDDINGS_SAMPLE_ROWS:", len(data))
    for row in data:
        print({
            "sender_id": row.get("sender_id"),
            "message": str(row.get("message"))[:220],
            "metadata_keys": list((row.get("metadata") or {}).keys()) if isinstance(row.get("metadata"), dict) else None
        })
else:
    print("NEURA_EMBEDDINGS_SAMPLE_ERROR:", data)

print("\n===== VERDICT =====")
print("If neura_embeddings TABLE_OK and has rows: REST storage exists, but PgVector SQL still needs DATABASE_URL.")
print("If config hits contain DATABASE_URL/OpenAI: copy manually into .env after checking source.")
print("P4.65K_COMPLETE")
