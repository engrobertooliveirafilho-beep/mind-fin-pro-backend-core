import os, json, time

class EldoraPersistenceProvider:
    def __init__(self):
        self.database_url_present = bool(os.getenv("DATABASE_URL"))
        self.supabase_url_present = bool(os.getenv("SUPABASE_URL"))

    def health(self):
        return {
            "provider": "supabase_postgres_ready",
            "database_url_present": self.database_url_present,
            "supabase_url_present": self.supabase_url_present,
            "live_connection_declared": False
        }

    def build_event(self, tenant_id, user_id, event_type, payload=None, idempotency_key=None):
        return {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "event_type": event_type,
            "payload": payload or {},
            "idempotency_key": idempotency_key or f"{tenant_id}:{user_id}:{event_type}:{int(time.time())}"
        }
