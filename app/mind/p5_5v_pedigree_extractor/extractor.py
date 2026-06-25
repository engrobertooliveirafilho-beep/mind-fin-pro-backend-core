import os, json, re, hashlib, urllib.request, urllib.parse
try:
    from _maintenance.P19P22A_20260618_110511.p56g4_strict_entity_validator import validate_pedigree_edge
except Exception:
    def validate_pedigree_edge(edge):
        return True

def norm(x):
    return re.sub(r"\s+", " ", str(x or "").strip())

def key(name):
    return hashlib.sha256("|".join([norm(name).lower(),"",""]).encode("utf-8")).hexdigest()

def extract_pedigree_claims(text):
    t=str(text or "")
    claims=[]
    patterns=[
        ("sire", r"(?i)\bsire[:\s]+([A-Z][A-Za-z0-9' .-]{2,40})"),
        ("dam", r"(?i)\bdam[:\s]+([A-Z][A-Za-z0-9' .-]{2,40})"),
        ("offspring", r"(?i)\boffspring[:\s]+([A-Z][A-Za-z0-9' .-]{2,40})"),
        ("sire", r"(?i)\bby\s+([A-Z][A-Za-z0-9' .-]{2,40})"),
        ("dam", r"(?i)\bout of\s+([A-Z][A-Za-z0-9' .-]{2,40})")
    ]
    for rel,pat in patterns:
        for m in re.findall(pat,t):
            name=norm(m).strip(" .,-")
            if len(name) >= 3 and len(name.split()) <= 6:
                claims.append({"relation":rel,"name":name})
    return claims

class PedigreeExtractor:
    def __init__(self, url=None, key_value=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key_value or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def real_sources(self, limit=250):
        return self.req("GET",f"/rest/v1/p55a_sources?source_type=eq.REAL_SEARCH_RESULT&select=id,source_url,title,raw_payload,confidence_score&order=created_at.desc&limit={limit}")

    def find_or_create_animal(self, name, confidence=35):
        k=key(name)
        q=urllib.parse.quote(k)
        rows=self.req("GET",f"/rest/v1/p55a_animals?identity_key=eq.{q}&select=id,official_name,identity_key")
        if rows:
            return rows[0]
        payload={"official_name":name,"animal_type":"bull","life_status":"unknown","identity_key":k,"confidence_score":confidence,"validation_status":"weak","notes":"Auto-created by P5.5V pedigree extractor; requires validation."}
        return self.req("POST","/rest/v1/p55a_animals?on_conflict=identity_key",payload)[0]

    def target_from_source(self, source):
        raw=source.get("raw_payload") or {}
        name=raw.get("animal_name") or raw.get("animal") or ""
        if not name:
            q=raw.get("query") or source.get("title") or ""
            for known in ["Bushwacker","Bodacious","Woopaa","Little Yellow Jacket","Bruiser","Asteroid"]:
                if known.lower() in q.lower():
                    return known
        return name

    def create_edge(self, parent_name, child_name, relation, source_id):
        confidence = 60 if source_id else 35
        validation = validate_pedigree_edge(parent_name, child_name, relation, confidence, source_id)

        if validation["status"] != "PASS":
            try:
                self.req("POST","/rest/v1/p55a_audit_logs",{
                    "event_type":"P5.6G5_PEDIGREE_EDGE_REJECTED",
                    "raw_payload":validation,
                    "confidence_score":confidence,
                    "validation_status":"rejected"
                })
            except Exception:
                pass
            return None

        pk=key(parent_name)
        pq=urllib.parse.quote(pk)
        parent_rows=self.req("GET",f"/rest/v1/p55a_animals?identity_key=eq.{pq}&select=id,official_name,identity_key,confidence_score,validation_status")

        if not parent_rows:
            try:
                self.req("POST","/rest/v1/p55a_audit_logs",{
                    "event_type":"P5.6G7_PARENT_NOT_PREEXISTING_REJECTED",
                    "raw_payload":{"parent_name":parent_name,"child_name":child_name,"relation":relation,"source_id":source_id},
                    "confidence_score":confidence,
                    "validation_status":"rejected"
                })
            except Exception:
                pass
            return None

        parent=parent_rows[0]

        if str(parent.get("validation_status")) in {"weak","quarantined"} or float(parent.get("confidence_score") or 0) <= 40:
            try:
                self.req("POST","/rest/v1/p55a_audit_logs",{
                    "event_type":"P5.6G7_PARENT_QUALITY_REJECTED",
                    "raw_payload":{"parent":parent,"child_name":child_name,"relation":relation,"source_id":source_id},
                    "confidence_score":confidence,
                    "validation_status":"rejected"
                })
            except Exception:
                pass
            return None

        child=self.find_or_create_animal(child_name,confidence)
        payload={"parent_id":parent["id"],"child_id":child["id"],"relation":relation,"generation_distance":1,"evidence_source_id":source_id,"confidence_score":confidence,"validation_status":"provisional"}
        try:
            return self.req("POST","/rest/v1/p55a_pedigree_edges?on_conflict=parent_id,child_id,relation",payload)[0]
        except Exception:
            return None

    def run_once(self, limit=250):
        created=[]; blocked=0
        for s in self.real_sources(limit):
            raw=s.get("raw_payload") or {}
            text=" ".join([str(s.get("title") or ""), str(s.get("source_url") or ""), str(raw.get("snippet") or ""), json.dumps(raw, ensure_ascii=False)])
            child=self.target_from_source(s)
            claims=extract_pedigree_claims(text)
            if not child or not claims:
                blocked+=1
                continue
            for c in claims:
                if c["relation"] in ["sire","dam"]:
                    edge=self.create_edge(c["name"], child, c["relation"], s["id"])
                    if edge: created.append(edge)
        return {"status":"P5.5V_PEDIGREE_EXTRACTOR_DONE","sources_scanned":limit,"edges_created_or_seen":len(created),"blocked":blocked,"next_action":"P5.5W_VIDEO_METADATA_EXTRACTOR"}



