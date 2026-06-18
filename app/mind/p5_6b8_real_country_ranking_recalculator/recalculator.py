import os, json, urllib.request, urllib.parse
from collections import defaultdict

def avg(xs):
    xs=[float(x or 0) for x in xs]
    return round(sum(xs)/len(xs),4) if xs else 0

class RealCountryRankingRecalculator:
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

    def run_once(self):
        animals=self.req("GET","/rest/v1/p55a_animals?select=id,country,official_name")
        country_by_id={a["id"]:(a.get("country") or "Unknown") for a in animals}
        vals=self.req("GET","/rest/v1/p55a_valuation_events?event_type=eq.P5.6B6_REAL_VALUATION&select=animal_id,amount,raw_payload&limit=10000")

        grouped=defaultdict(lambda: {"scores":[],"judge":[],"bio":[],"media":0,"animals":set()})
        for v in vals:
            c=country_by_id.get(v["animal_id"],"Unknown")
            rp=v.get("raw_payload") or {}
            grouped[c]["scores"].append(v.get("amount"))
            grouped[c]["judge"].append(rp.get("avg_judge_score"))
            grouped[c]["bio"].append(rp.get("avg_biomechanics_score"))
            grouped[c]["media"] += int(rp.get("media_count") or 0)
            grouped[c]["animals"].add(v["animal_id"])

        written=[]
        for c,g in grouped.items():
            cq=urllib.parse.quote(c, safe="")
            old=self.req("GET",f"/rest/v1/p55a_country_rankings?country=eq.{cq}&select=id")
            for r in old:
                self.req("DELETE",f"/rest/v1/p55a_country_rankings?id=eq.{r['id']}")

            payload={
                "country":c,
                "strength":avg(g["bio"]),
                "spin":0,
                "explosion":0,
                "kick":0,
                "difficulty":avg(g["judge"]),
                "consistency":0,
                "buckoff_capacity":avg(g["judge"]),
                "genetic_production":len(g["animals"]),
                "commercial_value":avg(g["scores"]),
                "pedigree_depth":0,
                "documented_volume":g["media"],
                "global_score":round(avg(g["scores"]) + min(g["media"]*0.25,25) + min(len(g["animals"])*2,20),4)
            }
            written.append(self.req("POST","/rest/v1/p55a_country_rankings",payload)[0])

        return {"status":"P5.6B8_REAL_COUNTRY_RANKING_RECALCULATED","countries":len(written),"ranking":sorted(written,key=lambda x:x["global_score"],reverse=True)}
