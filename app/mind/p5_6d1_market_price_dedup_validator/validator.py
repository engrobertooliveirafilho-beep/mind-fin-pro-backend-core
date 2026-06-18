import os, json, urllib.request, urllib.parse
from collections import defaultdict

class MarketPriceDedupValidator:
    def __init__(self,url=None,key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self,method,path,payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def market_events(self):
        return self.req("GET","/rest/v1/p55a_valuation_events?event_type=eq.P5.6D_MARKET_PRICE&select=*&limit=10000")

    def delete(self,eid):
        return self.req("DELETE",f"/rest/v1/p55a_valuation_events?id=eq.{eid}")

    def patch(self,eid,payload):
        return self.req("PATCH",f"/rest/v1/p55a_valuation_events?id=eq.{eid}",payload)

    def run_once(self):
        rows=self.market_events()
        groups=defaultdict(list)
        deleted=[]
        patched=[]

        for r in rows:
            key=(r.get("animal_id"),r.get("source_id"),float(r.get("amount") or 0))
            groups[key].append(r)

        for key,items in groups.items():
            keep=items[0]
            for extra in items[1:]:
                self.delete(extra["id"])
                deleted.append(extra["id"])

            rp=keep.get("raw_payload") or {}
            name=str(rp.get("official_name") or "").lower()
            source_text=" ".join([str(rp.get("source_title") or ""),str(rp.get("source_url") or "")]).lower()
            strong_name = name and name in source_text

            new_status="validated" if strong_name else "needs_review"
            new_conf=70 if strong_name else 45
            patched.append(self.patch(keep["id"],{"validation_status":new_status,"confidence_score":new_conf})[0])

        return {
            "status":"P5.6D1_MARKET_PRICE_DEDUP_VALIDATED",
            "events_scanned":len(rows),
            "events_kept":len(patched),
            "duplicates_deleted":len(deleted),
            "validated":sum(1 for x in patched if x.get("validation_status")=="validated"),
            "needs_review":sum(1 for x in patched if x.get("validation_status")=="needs_review")
        }
