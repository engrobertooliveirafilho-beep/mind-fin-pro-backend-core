import os, json, urllib.request
from fastapi import APIRouter

router = APIRouter(prefix="/p55/bulls", tags=["P5.5 Bulls Audit"])

TABLES = [
    "p55a_animals","p55a_sources","p55a_pedigree_edges","p55a_media",
    "p55a_biomechanics","p55a_judge_scores","p55a_valuation_events",
    "p55a_reproduction_records","p55a_country_rankings","p55a_audit_logs"
]

class P55Audit:
    def __init__(self):
        self.url=os.getenv("SUPABASE_URL","").rstrip("/")
        self.key=os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, path):
        r=urllib.request.Request(self.url+path,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}"},method="GET")
        with urllib.request.urlopen(r,timeout=30) as x:
            return json.loads(x.read().decode("utf-8"))

    def count(self, table):
        return len(self.req(f"/rest/v1/{table}?select=id&limit=10000"))

    def run(self):
        counts={t:self.count(t) for t in TABLES}
        gaps=[]
        if counts["p55a_animals"] < 1000: gaps.append("base_animals_small")
        if counts["p55a_media"] < counts["p55a_animals"]: gaps.append("media_coverage_low")
        if counts["p55a_biomechanics"] < counts["p55a_media"]: gaps.append("biomechanics_missing")
        if counts["p55a_judge_scores"] < counts["p55a_media"]: gaps.append("judge_scores_missing")
        if counts["p55a_reproduction_records"] == 0: gaps.append("reproduction_records_empty")
        if counts["p55a_country_rankings"] == 0: gaps.append("country_rankings_empty")
        return {"status":"P5.5O_AUDIT_READY","counts":counts,"critical_gaps":gaps,"next_action":"P5.5P_REAL_WEB_COLLECTOR"}

@router.get("/audit")
def p55_bulls_audit():
    return P55Audit().run()
