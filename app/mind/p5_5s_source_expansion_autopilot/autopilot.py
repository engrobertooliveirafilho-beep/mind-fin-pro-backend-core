import os, json, hashlib, urllib.request, urllib.parse

EXPANSION_TEMPLATES = [
    ("PEDIGREE_SEARCH", "{name} bucking bull pedigree sire dam offspring"),
    ("SEMEN_MARKET_SEARCH", "{name} bucking bull semen price"),
    ("AUCTION_SEARCH", "{name} bucking bull auction sale price"),
    ("VIDEO_SEARCH", "{name} PBR bull ride official score video"),
    ("OFFSPRING_SEARCH", "{name} bucking bull offspring champions"),
    ("HISTORY_SEARCH", "{name} rodeo bull history biography")
]

def evidence_hash(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()

class SourceExpansionAutopilot:
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
            headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"},
            method=method
        )
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def animals(self, limit=100):
        return self.req("GET",f"/rest/v1/p55a_animals?select=id,official_name,country,confidence_score&order=created_at.desc&limit={limit}")

    def build_source(self, animal, source_type, query):
        url="https://www.google.com/search?q="+urllib.parse.quote(query)
        payload={
            "source_url":url,
            "source_type":source_type,
            "title":f"P5.5S expansion: {query}",
            "platform":"search",
            "raw_payload":{"mission":"P5.5S","animal_id":animal["id"],"animal_name":animal["official_name"],"query":query},
            "confidence_score":45,
            "validation_status":"provisional"
        }
        payload["evidence_hash"]=evidence_hash({"url":url,"type":source_type,"animal_id":animal["id"]})
        return payload

    def expand_for_animal(self, animal):
        return [self.build_source(animal, st, tpl.format(name=animal["official_name"])) for st,tpl in EXPANSION_TEMPLATES]

    def run_once(self, limit=100):
        generated=[]
        for a in self.animals(limit):
            generated.extend(self.expand_for_animal(a))
        rows=[]
        for g in generated:
            rows.append(self.req("POST","/rest/v1/p55a_sources?on_conflict=evidence_hash",g)[0])
        return {
            "status":"P5.5S_SOURCE_EXPANSION_AUTOPILOT_DONE",
            "animals_scanned":len(self.animals(limit)),
            "generated":len(generated),
            "upserted":len(rows),
            "unique_hashes":len(set(r["evidence_hash"] for r in rows)),
            "next_action":"P5.5T_REAL_FETCHER_OR_SEARCH_API_CONNECTOR"
        }
