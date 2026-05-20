import os, json, urllib.request, urllib.parse

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""

def _supabase_enabled():
    return bool(SUPABASE_URL and SUPABASE_KEY)

def _headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

def _extract_sender_id(history):
    for row in history or []:
        sender = row.get("sender_id") or row.get("from") or row.get("From")
        if sender:
            return str(sender)
    return None

def _fetch_neura_memory(sender_id, limit=8):
    if not (_supabase_enabled() and sender_id):
        return []
    try:
        sender_q = urllib.parse.quote(str(sender_id), safe="")
        url = f"{SUPABASE_URL}/rest/v1/neura_memory?select=content,memory_type,created_at&sender_id=eq.{sender_q}&order=created_at.desc&limit={int(limit)}"
        req = urllib.request.Request(url, headers=_headers(), method="GET")
        return json.loads(urllib.request.urlopen(req, timeout=8).read().decode("utf-8"))
    except Exception:
        return []

class RetrievalProvider:
    def retrieve(self, message=None, history=None):
        query = message or ""
        ctx = self.build_context(history or [])
        direct = self.search(query, ctx)
        merged = dict(ctx)
        merged["facts"].update(direct.get("facts", {}))
        merged["query"] = query
        merged["source"] = "retrieval_provider_supabase_neura_memory_v1"
        return merged

    def build_context(self, history=None):
        facts = {}
        lines = []
        sender_id = _extract_sender_id(history or [])
        persistent_rows = _fetch_neura_memory(sender_id)

        for row in persistent_rows:
            text = (row.get("content") or "").strip()
            if text:
                lines.append(text)

        for row in history or []:
            text = (row.get("message") or row.get("content") or "").strip()
            if text:
                lines.append(text)

        for text in lines:
            low = text.lower()
            if "roberto" in low:
                facts["name"] = "Roberto"
            if "diesel" in low:
                facts["topic"] = "motor diesel"
            elif "carro" in low or "carros" in low:
                facts["topic"] = "carros"
            elif "implant" in low or "eldora" in low or "humaniza" in low:
                facts["topic"] = "implantações Eldora"
            elif "matem" in low or "math" in low:
                facts["topic"] = "tema técnico"

        return {
            "facts": facts,
            "history_text": "\n".join(lines[-20:]),
            "history_count": len(lines),
            "persistent_memory_count": len(persistent_rows),
            "sender_id": sender_id,
        }

    def search(self, query: str = "", context: dict | None = None) -> dict:
        text = (query or "").lower()
        facts = {}

        if "roberto" in text:
            facts["name"] = "Roberto"

        if "ram 2500" in text or "ram 3500" in text:
            facts["topic"] = "comparativo RAM 2500 vs RAM 3500"
        elif "diesel" in text:
            facts["topic"] = "motor diesel"
        elif "carro" in text or "carros" in text:
            facts["topic"] = "carros"
        elif "implant" in text or "eldora" in text or "humaniza" in text:
            facts["topic"] = "implantações Eldora"
        elif "math" in text or "matem" in text:
            facts["topic"] = "tema técnico"

        return {"query": query, "facts": facts, "context": context or {}, "source": "query_heuristic"}
