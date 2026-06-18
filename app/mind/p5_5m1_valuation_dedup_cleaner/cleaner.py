import os, json, urllib.request, urllib.parse

class ValuationDedupCleaner:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(
            self.url+path,
            data=data,
            headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},
            method=method
        )
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def valuations(self):
        return self.req("GET","/rest/v1/p55a_valuation_events?event_type=eq.P5.5K_INITIAL_VALUATION&select=id,animal_id,amount,created_at,raw_payload&order=amount.desc")

    def delete(self, row_id):
        q=urllib.parse.quote(row_id)
        return self.req("DELETE",f"/rest/v1/p55a_valuation_events?id=eq.{q}")

    def clean(self):
        groups={}
        for v in self.valuations():
            groups.setdefault(v["animal_id"], []).append(v)

        deleted=[]
        kept=[]
        for animal_id, rows in groups.items():
            rows=sorted(rows, key=lambda r: (float(r.get("amount") or 0), r.get("created_at") or ""), reverse=True)
            kept.append(rows[0])
            for dup in rows[1:]:
                self.delete(dup["id"])
                deleted.append(dup["id"])

        return {
            "status":"P5.5M1_VALUATION_DEDUP_DONE",
            "groups":len(groups),
            "kept":len(kept),
            "deleted":len(deleted),
            "deleted_ids":deleted
        }
