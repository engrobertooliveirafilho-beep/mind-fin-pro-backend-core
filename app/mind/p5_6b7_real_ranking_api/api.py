import os, json, urllib.request

class RealRankingAPI:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path):
        r=urllib.request.Request(self.url+path,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def ranking(self, limit=20):
        rows=self.req("GET",f"/rest/v1/p55a_valuation_events?event_type=eq.P5.6B6_REAL_VALUATION&select=animal_id,amount,raw_payload,confidence_score,created_at&order=amount.desc&limit={limit}")
        return {
            "status":"P5.6B7_REAL_RANKING_READY",
            "system":"GLOBAL_BOVINE_SPORTS_GENETICS_INTELLIGENCE_SYSTEM",
            "ranking_type":"real_cv_judge_valuation",
            "count":len(rows),
            "ranking":[
                {
                    "rank":i+1,
                    "animal_id":r["animal_id"],
                    "name":(r.get("raw_payload") or {}).get("official_name"),
                    "score":r.get("amount"),
                    "avg_judge_score":(r.get("raw_payload") or {}).get("avg_judge_score"),
                    "avg_biomechanics_score":(r.get("raw_payload") or {}).get("avg_biomechanics_score"),
                    "media_count":(r.get("raw_payload") or {}).get("media_count"),
                    "pedigree_edges":(r.get("raw_payload") or {}).get("pedigree_edges"),
                    "confidence":(r.get("raw_payload") or {}).get("confidence"),
                    "valuation_formula":(r.get("raw_payload") or {}).get("valuation_formula")
                }
                for i,r in enumerate(rows)
            ]
        }
