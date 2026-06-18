import os, json, hashlib, urllib.request, urllib.parse, re
from datetime import datetime, timezone

SEED_ANIMALS = ["Bushwacker","Bodacious","Woopaa","Little Yellow Jacket","Bruiser","Asteroid"]

QUERY_TEMPLATES = [
    "{name} PBR bull official score",
    "{name} ABBI pedigree bucking bull",
    "{name} rodeo bull semen auction",
    "{name} bull ride YouTube",
    "{name} bucking bull offspring",
    "{name} PRCA NFR bull"
]

SOURCE_TYPES = ["SEARCH_QUERY","YOUTUBE_SEARCH","PBR_SEARCH","ABBI_SEARCH","AUCTION_SEARCH"]

def now(): return datetime.now(timezone.utc).isoformat()

def h(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()

def norm(x):
    return re.sub(r"\s+"," ",str(x or "").strip())

class GlobalWebAbsorptionRuntime:
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

    def source_record(self, animal, query, source_type):
        url="https://www.google.com/search?q="+urllib.parse.quote(query)
        payload={
            "source_url":url,
            "source_type":source_type,
            "title":f"P5.5P discovery query: {query}",
            "platform":"search",
            "raw_payload":{"mission":"P5.5P","animal":animal,"query":query,"runtime":"GLOBAL_WEB_ABSORPTION_RUNTIME"},
            "confidence_score":50,
            "validation_status":"provisional"
        }
        payload["evidence_hash"]=h({"source_url":url,"source_type":source_type,"query":query})
        return payload

    def expand_queries(self, animals=None):
        animals=animals or SEED_ANIMALS
        out=[]
        for animal in animals:
            for i,t in enumerate(QUERY_TEMPLATES):
                source_type=SOURCE_TYPES[i % len(SOURCE_TYPES)]
                out.append(self.source_record(animal, t.format(name=animal), source_type))
        return out

    def upsert_sources(self, rows):
        inserted=[]
        for row in rows:
            inserted.append(self.req("POST","/rest/v1/p55a_sources?on_conflict=evidence_hash",row)[0])
        return inserted

    def run_once(self, animals=None):
        rows=self.expand_queries(animals)
        inserted=self.upsert_sources(rows)
        return {
            "status":"P5.5P_GLOBAL_WEB_ABSORPTION_RUNTIME_DONE",
            "generated":len(rows),
            "upserted":len(inserted),
            "unique_hashes":len(set(r.get("evidence_hash") for r in inserted)),
            "next_action":"P5.5Q_WORKER_FETCH_AND_PARSE"
        }
