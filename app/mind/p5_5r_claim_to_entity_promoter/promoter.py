import os, json, urllib.request, urllib.parse, hashlib, re

KNOWN_ANIMALS = ["Bushwacker","Bodacious","Woopaa","Little Yellow Jacket","Bruiser","Asteroid"]

def norm(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())

def identity_key(name, registry_number=None, birth_year=None):
    seed="|".join([norm(name), str(registry_number or ""), str(birth_year or "")])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()

def detect_animals(text):
    t=str(text or "").lower()
    return [a for a in KNOWN_ANIMALS if a.lower() in t]

class ClaimToEntityPromoter:
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

    def sources(self, limit=100):
        return self.req("GET",f"/rest/v1/p55a_sources?select=id,source_url,source_type,title,raw_payload,confidence_score,validation_status&order=created_at.desc&limit={limit}")

    def promote_animal(self, name, source):
        payload={
            "official_name":name,
            "aliases":[name],
            "animal_type":"bull",
            "life_status":"unknown",
            "identity_key":identity_key(name),
            "confidence_score":max(40, min(75, float(source.get("confidence_score") or 40))),
            "validation_status":"provisional",
            "notes":"Promoted by P5.5R from source claim; still requires source-level validation."
        }
        row=self.req("POST","/rest/v1/p55a_animals?on_conflict=identity_key",payload)[0]
        self.audit(row["id"], source["id"], name)
        return row

    def audit(self, animal_id, source_id, name):
        payload={
            "entity_type":"animal",
            "entity_id":animal_id,
            "audit_type":"P5.5R_CLAIM_PROMOTED_TO_ANIMAL",
            "confidence_score":55,
            "evidence_count":1,
            "source_count":1,
            "conflict_count":0,
            "missing_fields":["official_source_validation_pending"],
            "contradictions":[],
            "audit_status":"provisional"
        }
        return self.req("POST","/rest/v1/p55a_audit_logs",payload)

    def run_once(self, limit=100):
        promoted=[]
        blocked=[]
        for s in self.sources(limit):
            text=" ".join([str(s.get("title") or ""), str(s.get("source_url") or ""), json.dumps(s.get("raw_payload") or {}, ensure_ascii=False)])
            animals=detect_animals(text)
            if not animals:
                blocked.append({"source_id":s["id"],"reason":"no_known_animal_detected"})
                continue
            for name in animals:
                promoted.append(self.promote_animal(name,s))
        return {
            "status":"P5.5R_CLAIM_TO_ENTITY_PROMOTER_DONE",
            "sources_scanned":limit,
            "promoted":len(promoted),
            "blocked":len(blocked),
            "unique_promoted_animals":len(set(x["identity_key"] for x in promoted)),
            "next_action":"P5.5S_SOURCE_EXPANSION_AUTOPILOT"
        }
