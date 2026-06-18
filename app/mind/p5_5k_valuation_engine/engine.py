import os, json, urllib.request, urllib.parse

def valuation_score(judge=0, biomechanics=0, pedigree_edges=0, media_count=0, confidence=0):
    return round(min(100, float(judge)*0.35 + float(biomechanics)*0.30 + min(pedigree_edges*8,20) + min(media_count*5,15) + float(confidence)*0.10), 4)

class ValuationEngine:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key: raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x: return json.loads(x.read().decode("utf-8"))

    def animals(self):
        return self.req("GET","/rest/v1/p55a_animals?select=id,official_name,confidence_score&limit=100")

    def count(self, table, field, value):
        q=urllib.parse.quote(value)
        return len(self.req("GET",f"/rest/v1/{table}?{field}=eq.{q}&select=id"))

    def avg_biomechanics(self, animal_id):
        q=urllib.parse.quote(animal_id)
        rows=self.req("GET",f"/rest/v1/p55a_biomechanics?animal_id=eq.{q}&select=biomechanics_score")
        vals=[float(r["biomechanics_score"] or 0) for r in rows]
        return sum(vals)/len(vals) if vals else 0

    def avg_judge(self, animal_id):
        q=urllib.parse.quote(animal_id)
        rows=self.req("GET",f"/rest/v1/p55a_judge_scores?animal_id=eq.{q}&select=mind_bull_score")
        vals=[float(r["mind_bull_score"] or 0)*2 for r in rows]
        return sum(vals)/len(vals) if vals else 0

    def existing(self, animal_id):
        q=urllib.parse.quote(animal_id)
        rows=self.req("GET",f"/rest/v1/p55a_valuation_events?animal_id=eq.{q}&event_type=eq.P5.5K_INITIAL_VALUATION&select=id,animal_id,event_type,amount,raw_payload")
        return rows[0] if rows else None

    def value_animal(self, animal):
        existing=self.existing(animal["id"])
        if existing: return existing
        media=self.count("p55a_media","animal_id",animal["id"])
        pedigree=self.count("p55a_pedigree_edges","child_id",animal["id"])
        bio=self.avg_biomechanics(animal["id"])
        judge=self.avg_judge(animal["id"])
        conf=float(animal.get("confidence_score") or 0)
        score=valuation_score(judge,bio,pedigree,media,conf)
        payload={
            "animal_id":animal["id"],
            "event_type":"P5.5K_INITIAL_VALUATION",
            "currency":"SCORE",
            "amount":score,
            "raw_payload":{"mission":"P5.5K","official_name":animal.get("official_name"),"judge":judge,"biomechanics":bio,"pedigree_edges":pedigree,"media_count":media,"confidence":conf},
            "confidence_score":40,
            "validation_status":"provisional"
        }
        return self.req("POST","/rest/v1/p55a_valuation_events",payload)[0]

    def seed(self):
        return [self.value_animal(a) for a in self.animals()]

    def audit(self, rows):
        return {"status":"P5.5K_VALUATION_CREATED","total":len(rows),"unique_animals":len(set(r["animal_id"] for r in rows)),"ids":[r["id"] for r in rows]}
