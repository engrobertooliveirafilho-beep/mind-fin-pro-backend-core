import os, json, hashlib, urllib.request, re
from datetime import datetime, timezone

def normalize_name(name):
    return re.sub(r"\s+"," ",str(name or "").strip().lower())

def identity_key(payload):
    seed="|".join([
        normalize_name(payload.get("official_name")),
        str(payload.get("registry_number") or ""),
        str(payload.get("birth_year") or "")
    ])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()

REAL_BULL_CANDIDATES = [
 {"official_name":"Bushwacker","aliases":["Bushwacker"],"registry_number":"13/6","animal_type":"bull","sex":"male","country":"United States","birth_year":2006,"life_status":"alive","confidence_score":80,"validation_status":"reliable","notes":"Initial public candidate seed; requires source-level validation."},
 {"official_name":"Bodacious","aliases":["The World's Most Dangerous Bull"],"animal_type":"bull","sex":"male","country":"United States","birth_year":1988,"death_year":2000,"life_status":"deceased","confidence_score":80,"validation_status":"reliable","notes":"Initial public candidate seed; requires source-level validation."},
 {"official_name":"Woopaa","aliases":["Woopaa"],"animal_type":"bull","sex":"male","country":"United States","confidence_score":75,"validation_status":"reliable","notes":"Initial public candidate seed; requires source-level validation."},
 {"official_name":"Little Yellow Jacket","aliases":["Little Yellow Jacket"],"animal_type":"bull","sex":"male","country":"United States","confidence_score":75,"validation_status":"reliable","notes":"Initial public candidate seed; requires source-level validation."},
 {"official_name":"Bruiser","aliases":["SweetPro's Bruiser","Bruiser"],"animal_type":"bull","sex":"male","country":"United States","confidence_score":75,"validation_status":"reliable","notes":"Initial public candidate seed; requires source-level validation."},
 {"official_name":"Asteroid","aliases":["Asteroid"],"animal_type":"bull","sex":"male","country":"United States","confidence_score":75,"validation_status":"reliable","notes":"Initial public candidate seed; requires source-level validation."}
]

class BullCandidateIngestion:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY/ANON_KEY ausentes")

    def prepare(self, payload):
        p=dict(payload)
        p["identity_key"]=identity_key(p)
        return p

    def upsert_animal(self, payload):
        p=self.prepare(payload)
        req=urllib.request.Request(
            f"{self.url}/rest/v1/p55a_animals?on_conflict=identity_key",
            data=json.dumps(p).encode("utf-8"),
            headers={
                "apikey":self.key,
                "Authorization":f"Bearer {self.key}",
                "Content-Type":"application/json",
                "Prefer":"resolution=merge-duplicates,return=representation"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))

    def seed(self):
        rows=[]
        for item in REAL_BULL_CANDIDATES:
            rows.append(self.upsert_animal(item)[0])
        return rows

    def audit(self, rows):
        return {
            "status":"P5.5F_BULL_CANDIDATES_SEEDED",
            "total":len(rows),
            "unique_identity_keys":len(set(r.get("identity_key") for r in rows)),
            "ids":[r.get("id") for r in rows]
        }
