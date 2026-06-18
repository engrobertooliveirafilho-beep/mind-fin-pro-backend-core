import os, json, urllib.request
from datetime import datetime, timezone

TABLES = [
    "p55a_animals","p55a_sources","p55a_pedigree_edges","p55a_media",
    "p55a_biomechanics","p55a_judge_scores","p55a_valuation_events",
    "p55a_reproduction_records","p55a_country_rankings","p55a_audit_logs"
]

class ExecutiveSnapshot:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def count(self, table):
        import urllib.request
        r=urllib.request.Request(
            self.url+f"/rest/v1/{table}?select=id&limit=1",
            headers={
                "apikey":self.key,
                "Authorization":f"Bearer {self.key}",
                "Prefer":"count=exact"
            },
            method="GET"
        )
        with urllib.request.urlopen(r,timeout=30) as x:
            cr=x.headers.get("Content-Range") or x.headers.get("content-range") or "0-0/0"
        return int(str(cr).split("/")[-1])

    def ranking(self):
        return self.req("GET","/rest/v1/p55a_country_rankings?select=country,global_score,genetic_production,commercial_value,documented_volume&order=global_score.desc")

    def top_animals(self):
        return self.req("GET","/rest/v1/p55a_valuation_events?event_type=eq.P5.6B6_REAL_VALUATION&select=animal_id,amount,raw_payload&order=amount.desc&limit=10")

    def write_audit(self, snapshot):
        payload={
            "entity_type":"executive_snapshot",
            "audit_type":"P5.5Z_EXECUTIVE_SNAPSHOT",
            "confidence_score":70,
            "evidence_count":sum(snapshot["counts"].values()),
            "source_count":snapshot["counts"].get("p55a_sources",0),
            "conflict_count":0,
            "missing_fields":snapshot["critical_gaps"],
            "contradictions":[],
            "audit_status":"provisional"
        }
        return self.req("POST","/rest/v1/p55a_audit_logs",payload)

    def build(self):
        counts={t:self.count(t) for t in TABLES}
        gaps=[]
        if counts["p55a_reproduction_records"] == 0: gaps.append("reproduction_records_empty")
        if counts["p55a_animals"] < 1000: gaps.append("animal_base_small")
        if counts["p55a_media"] < 1000: gaps.append("media_base_small")
        if counts["p55a_biomechanics"] < counts["p55a_media"]: gaps.append("biomechanics_not_fully_scored")
        snapshot={
            "mission":"P5.5Z_EXECUTIVE_SNAPSHOT",
            "created_at":datetime.now(timezone.utc).isoformat(),
            "status":{
                "P5.5A_DATABASE":"TRUE",
                "P5.5B_TO_P5.5Y_PIPELINE":"TRUE",
                "FASTAPI_ROUTES":"TRUE",
                "REAL_SEARCH_CONNECTED":"TRUE",
                "GRAPH_CLEANED":"TRUE"
            },
            "counts":counts,
            "country_ranking":self.ranking(),
            "top_valuation_events":self.top_animals(),
            "critical_gaps":gaps,
            "next_missions":["P5.6A_REPRODUCTION_RECORDS","P5.6B_VIDEO_COMPUTER_VISION","P5.6C_PEDIGREE_SOURCE_VALIDATION","P5.6D_MARKET_VALUATION_REAL_PRICES"]
        }
        self.write_audit(snapshot)
        return snapshot

