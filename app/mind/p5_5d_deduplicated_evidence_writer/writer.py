import os, json, hashlib, urllib.request
from datetime import datetime, timezone
from urllib.parse import quote

def stable_hash(payload: dict) -> str:
    base = {
        "source_url": payload.get("source_url"),
        "source_type": payload.get("source_type"),
        "title": payload.get("title"),
        "raw_payload": payload.get("raw_payload", {})
    }
    return hashlib.sha256(json.dumps(base, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()

class DeduplicatedEvidenceWriter:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY/ANON_KEY ausentes")

    def prepare(self, payload: dict) -> dict:
        p=dict(payload)
        p.setdefault("captured_at", datetime.now(timezone.utc).isoformat())
        p.setdefault("confidence_score", 60)
        p.setdefault("validation_status", "provisional")
        p.setdefault("raw_payload", {})
        p["evidence_hash"]=stable_hash(p)
        return p

    def upsert_source(self, payload: dict):
        p=self.prepare(payload)
        endpoint=f"{self.url}/rest/v1/p55a_sources?on_conflict=evidence_hash"
        req=urllib.request.Request(
            endpoint,
            data=json.dumps(p).encode("utf-8"),
            headers={
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=representation"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))

    def query_by_hash(self, evidence_hash: str):
        endpoint=f"{self.url}/rest/v1/p55a_sources?evidence_hash=eq.{quote(evidence_hash)}&select=id,evidence_hash,source_url,title"
        req=urllib.request.Request(endpoint, headers={"apikey":self.key,"Authorization":f"Bearer {self.key}"}, method="GET")
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
