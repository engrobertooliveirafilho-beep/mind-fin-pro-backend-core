import os, json, time, uuid, urllib.request, urllib.parse

_MEMORY = {}

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""

def _enabled():
    return bool(SUPABASE_URL and SUPABASE_KEY)

def _headers(prefer="return=minimal"):
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h

def _safe_sender(sender_id):
    return str(sender_id or "default")[:180]

def _safe_key(key):
    return str(key or "short_memory")[:80]

def remember(key, value, sender_id="default", ttl=120):
    sender = _safe_sender(sender_id)
    mem_key = _safe_key(key)
    now = time.time()
    _MEMORY[(sender, mem_key)] = {"value": value, "expires": now + int(ttl)}

    if _enabled():
        row = {
            "id": str(uuid.uuid4()),
            "sender_id": sender,
            "memory_type": mem_key,
            "content": str(value or "")[:4000],
            "confidence": 0.95,
            "message": str(value or "")[:4000],
            "role": "short_memory",
        }
        try:
            req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/neura_memory",
                data=json.dumps(row).encode("utf-8"),
                headers=_headers(),
                method="POST",
            )
            urllib.request.urlopen(req, timeout=8).read()
            return {"ok": True, "backend": "supabase_neura_memory"}
        except Exception as e:
            return {"ok": True, "backend": "local_fallback", "supabase_error": str(e)[:240]}

    return {"ok": True, "backend": "local_fallback"}

def recall(key, sender_id="default"):
    sender = _safe_sender(sender_id)
    mem_key = _safe_key(key)

    if _enabled():
        try:
            sender_q = urllib.parse.quote(sender, safe="")
            key_q = urllib.parse.quote(mem_key, safe="")
            url = f"{SUPABASE_URL}/rest/v1/neura_memory?select=content,created_at&sender_id=eq.{sender_q}&memory_type=eq.{key_q}&order=created_at.desc&limit=1"
            req = urllib.request.Request(url, headers=_headers(prefer=None), method="GET")
            rows = json.loads(urllib.request.urlopen(req, timeout=8).read().decode("utf-8"))
            if rows:
                return rows[0].get("content")
        except Exception:
            pass

    item = _MEMORY.get((sender, mem_key))
    if not item:
        return None
    if item["expires"] < time.time():
        _MEMORY.pop((sender, mem_key), None)
        return None
    return item["value"]
