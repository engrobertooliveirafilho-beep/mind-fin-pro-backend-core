import os, json, urllib.request

class SupabaseIngestionWriter:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY/ANON_KEY ausentes")

    def insert(self, table, payload):
        req=urllib.request.Request(
            f"{self.url}/rest/v1/{table}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))

    def health_payload(self):
        return {"source_url":"https://pbr.com","source_type":"PBR","title":"P5.5C health seed","raw_payload":{"mission":"P5.5C"},"confidence_score":75,"validation_status":"reliable"}
