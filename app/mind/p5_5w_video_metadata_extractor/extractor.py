import os, json, re, hashlib, urllib.request, urllib.parse

KNOWN_ANIMALS = ["Bushwacker","Bodacious","Woopaa","Little Yellow Jacket","Bruiser","Asteroid"]

def norm(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())

def animal_key(name):
    return hashlib.sha256("|".join([norm(name),"",""]).encode("utf-8")).hexdigest()

def detect_video_signal(source):
    text=" ".join([str(source.get("title") or ""), str(source.get("source_url") or ""), json.dumps(source.get("raw_payload") or {}, ensure_ascii=False)]).lower()
    return any(x in text for x in ["youtube","video","bull ride","official score"])

def detect_animal(source):
    text=" ".join([str(source.get("title") or ""), str(source.get("source_url") or ""), json.dumps(source.get("raw_payload") or {}, ensure_ascii=False)]).lower()
    for a in KNOWN_ANIMALS:
        if a.lower() in text:
            return a
    raw=source.get("raw_payload") or {}
    return raw.get("animal_name") or raw.get("animal")

class VideoMetadataExtractor:
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

    def sources(self, limit=300):
        return self.req("GET",f"/rest/v1/p55a_sources?select=id,source_url,source_type,title,raw_payload,confidence_score,validation_status&order=created_at.desc&limit={limit}")

    def find_or_create_animal(self, name):
        k=animal_key(name)
        q=urllib.parse.quote(k)
        rows=self.req("GET",f"/rest/v1/p55a_animals?identity_key=eq.{q}&select=id,official_name,identity_key")
        if rows:
            return rows[0]
        payload={"official_name":name,"animal_type":"bull","life_status":"unknown","identity_key":k,"confidence_score":45,"validation_status":"provisional","notes":"Auto-created by P5.5W video metadata extractor."}
        return self.req("POST","/rest/v1/p55a_animals?on_conflict=identity_key",payload)[0]

    def media_exists(self, url):
        q=urllib.parse.quote(url, safe="")
        rows=self.req("GET",f"/rest/v1/p55a_media?url=eq.{q}&select=id,animal_id,source_id,url,title")
        return rows[0] if rows else None

    def create_media(self, source, animal_name):
        existing=self.media_exists(source["source_url"])
        if existing:
            return existing
        animal=self.find_or_create_animal(animal_name)
        payload={
            "animal_id":animal["id"],
            "source_id":source["id"],
            "url":source["source_url"],
            "platform":"youtube" if "youtube" in source["source_url"].lower() or "youtube" in str(source.get("title","")).lower() else "web_video_candidate",
            "title":source.get("title"),
            "event_name":"P5.5W video candidate",
            "result":"candidate_video_metadata",
            "metadata":{"mission":"P5.5W","source_type":source.get("source_type"),"animal_name":animal_name,"raw_payload":source.get("raw_payload")},
            "confidence_score":50,
            "validation_status":"provisional"
        }
        return self.req("POST","/rest/v1/p55a_media",payload)[0]

    def run_once(self, limit=300):
        created=[]; blocked=0
        for s in self.sources(limit):
            if not detect_video_signal(s):
                blocked+=1
                continue
            animal=detect_animal(s)
            if not animal:
                blocked+=1
                continue
            created.append(self.create_media(s,animal))
        return {"status":"P5.5W_VIDEO_METADATA_EXTRACTOR_DONE","sources_scanned":limit,"media_created_or_seen":len(created),"blocked":blocked,"next_action":"P5.5X_GENETIC_GRAPH_BUILDER"}
