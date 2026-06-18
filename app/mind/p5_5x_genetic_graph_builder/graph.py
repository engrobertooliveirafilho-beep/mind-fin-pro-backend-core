import os, json, urllib.request
from collections import defaultdict

class GeneticGraphBuilder:
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
            headers={
                "apikey":self.key,
                "Authorization":f"Bearer {self.key}",
                "Content-Type":"application/json",
                "Prefer":"return=representation"
            },
            method=method
        )
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def animals(self):
        return self.req("GET","/rest/v1/p55a_animals?select=id,official_name")

    def edges(self):
        return self.req("GET","/rest/v1/p55a_pedigree_edges?select=parent_id,child_id,relation,confidence_score")

    def build(self):
        animals={a["id"]:a for a in self.animals()}
        indeg=defaultdict(int)
        outdeg=defaultdict(int)

        for e in self.edges():
            outdeg[e["parent_id"]] += 1
            indeg[e["child_id"]] += 1

        ranking=[]
        for aid,a in animals.items():
            influence=(outdeg[aid]*3)+(indeg[aid]*1)
            ranking.append({
                "animal_id":aid,
                "official_name":a["official_name"],
                "influence_score":influence,
                "children":outdeg[aid],
                "ancestors":indeg[aid]
            })

        ranking=sorted(ranking,key=lambda x:x["influence_score"],reverse=True)

        return ranking

    def write_audit(self, top):
        payload={
            "entity_type":"genetic_graph",
            "audit_type":"P5.5X_GENETIC_GRAPH",
            "confidence_score":60,
            "evidence_count":len(top),
            "source_count":1,
            "conflict_count":0,
            "missing_fields":[],
            "contradictions":[],
            "audit_status":"provisional"
        }
        return self.req("POST","/rest/v1/p55a_audit_logs",payload)

    def run_once(self):
        ranking=self.build()
        self.write_audit(ranking[:25])

        return {
            "status":"P5.5X_GENETIC_GRAPH_BUILDER_DONE",
            "animals":len(ranking),
            "top_founders":ranking[:10],
            "next_action":"P5.5Y_COUNTRY_COMPARATOR"
        }

