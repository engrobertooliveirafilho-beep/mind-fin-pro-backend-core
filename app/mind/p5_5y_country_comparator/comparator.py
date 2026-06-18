import os, json, urllib.request
from collections import defaultdict

def avg(vals):
    vals=[float(v or 0) for v in vals]
    return round(sum(vals)/len(vals),4) if vals else 0

class CountryComparator:
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

    def animals(self):
        return self.req("GET","/rest/v1/p55a_animals?select=id,official_name,country")

    def count_by(self, table, field, value):
        return len(self.req("GET",f"/rest/v1/{table}?{field}=eq.{value}&select=id"))

    def valuations(self):
        return self.req("GET","/rest/v1/p55a_valuation_events?select=animal_id,amount")

    def biomechanics(self):
        return self.req("GET","/rest/v1/p55a_biomechanics?select=animal_id,biomechanics_score,difficulty_score,kick_score,explosiveness_score,consistency_score")

    def build(self):
        animals=self.animals()
        country_by_animal={a["id"]:(a.get("country") or "Unknown") for a in animals}
        grouped=defaultdict(lambda: {"animals":0,"valuations":[],"bio":[],"difficulty":[],"kick":[],"explosion":[],"consistency":[]})

        for a in animals:
            grouped[country_by_animal[a["id"]]]["animals"] += 1

        for v in self.valuations():
            c=country_by_animal.get(v["animal_id"],"Unknown")
            grouped[c]["valuations"].append(v.get("amount") or 0)

        for b in self.biomechanics():
            c=country_by_animal.get(b["animal_id"],"Unknown")
            grouped[c]["bio"].append(b.get("biomechanics_score") or 0)
            grouped[c]["difficulty"].append(b.get("difficulty_score") or 0)
            grouped[c]["kick"].append(b.get("kick_score") or 0)
            grouped[c]["explosion"].append(b.get("explosiveness_score") or 0)
            grouped[c]["consistency"].append(b.get("consistency_score") or 0)

        rows=[]
        for country,g in grouped.items():
            row={
                "country":country,
                "strength":avg(g["bio"]),
                "spin":0,
                "explosion":avg(g["explosion"]),
                "kick":avg(g["kick"]),
                "difficulty":avg(g["difficulty"]),
                "consistency":avg(g["consistency"]),
                "buckoff_capacity":avg(g["difficulty"]),
                "genetic_production":g["animals"],
                "commercial_value":avg(g["valuations"]),
                "pedigree_depth":0,
                "documented_volume":g["animals"],
                "global_score":round(avg(g["bio"])*0.35 + avg(g["valuations"])*0.25 + min(g["animals"]*5,40),4)
            }
            rows.append(row)
        return sorted(rows,key=lambda x:x["global_score"],reverse=True)

    def clear_today(self, country):
        return self.req("DELETE",f"/rest/v1/p55a_country_rankings?country=eq.{country}")

    def run_once(self):
        rows=self.build()
        written=[]
        for r in rows:
            country=r["country"].replace("'","")
            try: self.clear_today(country)
            except Exception: pass
            written.append(self.req("POST","/rest/v1/p55a_country_rankings",r)[0])
        return {"status":"P5.5Y_COUNTRY_COMPARATOR_DONE","countries":len(written),"ranking":written,"next_action":"P5.5Z_EXECUTIVE_SNAPSHOT"}
