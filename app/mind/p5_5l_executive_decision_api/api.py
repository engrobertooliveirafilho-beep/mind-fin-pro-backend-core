import os, json, urllib.request

QUESTION_TYPES = [
    "which_bull_to_buy",
    "which_semen_to_buy",
    "which_lineage_to_follow",
    "undervalued_genetics",
    "overvalued_genetics",
    "global_valuation_ranking"
]

class ExecutiveDecisionAPI:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, path):
        r=urllib.request.Request(self.url+path,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}"},method="GET")
        with urllib.request.urlopen(r,timeout=30) as x:
            return json.loads(x.read().decode("utf-8"))

    def valuations(self):
        return self.req("/rest/v1/p55a_valuation_events?event_type=eq.P5.5K_INITIAL_VALUATION&select=id,animal_id,amount,confidence_score,raw_payload&order=amount.desc")

    def animal(self, animal_id):
        rows=self.req(f"/rest/v1/p55a_animals?id=eq.{animal_id}&select=id,official_name,aliases,country,life_status,confidence_score,validation_status")
        return rows[0] if rows else {}

    def ranking(self, limit=10):
        out=[]
        for v in self.valuations()[:limit]:
            a=self.animal(v["animal_id"])
            out.append({"animal_id":v["animal_id"],"name":a.get("official_name"),"country":a.get("country"),"life_status":a.get("life_status"),"valuation_score":v.get("amount"),"confidence_score":v.get("confidence_score"),"evidence":v.get("raw_payload")})
        return out

    def decide(self, question_type="global_valuation_ranking", limit=5):
        if question_type not in QUESTION_TYPES:
            question_type="global_valuation_ranking"
        rank=self.ranking(limit)
        return {"status":"P5.5L_EXECUTIVE_DECISION_READY","question_type":question_type,"recommendation":rank[0] if rank else None,"alternatives":rank[1:],"risk":"Base inicial pequena; recomendações provisórias até ampliar fontes, vídeos, pedigree e notas oficiais.","next_action":"Expandir ingestão real de fontes e substituir scores placeholder por métricas extraídas de vídeo.","confidence":"provisional"}
