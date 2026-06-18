import os, json, urllib.request, urllib.parse, hashlib, re

def norm(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())

def animal_key(name, registry_number=None, birth_year=None):
    return hashlib.sha256("|".join([norm(name), str(registry_number or ""), str(birth_year or "")]).encode("utf-8")).hexdigest()

MEDIA_EVENT_SEEDS = [
    {"animal_name":"Bushwacker","url":"https://www.youtube.com/results?search_query=Bushwacker+PBR+official+score","platform":"youtube","title":"Bushwacker PBR official score search","event_name":"PBR public video search","result":"candidate_media","buckoff":None,"confidence_score":55,"validation_status":"provisional"},
    {"animal_name":"Bodacious","url":"https://www.youtube.com/results?search_query=Bodacious+bull+ride","platform":"youtube","title":"Bodacious bull ride search","event_name":"historic public video search","result":"candidate_media","buckoff":None,"confidence_score":55,"validation_status":"provisional"},
    {"animal_name":"Woopaa","url":"https://www.youtube.com/results?search_query=Woopaa+PBR+score","platform":"youtube","title":"Woopaa PBR score search","event_name":"PBR public video search","result":"candidate_media","buckoff":None,"confidence_score":55,"validation_status":"provisional"}
]

class MediaEventIngestion:
    def __init__(self, url=None, key=None):
        self.url = (url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.key = key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            self.url + path,
            data=data,
            headers={
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=representation"
            },
            method=method
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def find_animal(self, name):
        q = urllib.parse.quote(animal_key(name))
        rows = self.req("GET", f"/rest/v1/p55a_animals?identity_key=eq.{q}&select=id,official_name,identity_key")
        if rows:
            return rows[0]
        payload = {
            "official_name": name,
            "animal_type": "bull",
            "life_status": "unknown",
            "identity_key": animal_key(name),
            "confidence_score": 40,
            "validation_status": "weak",
            "notes": "Auto-created by P5.5H media seed."
        }
        return self.req("POST", "/rest/v1/p55a_animals?on_conflict=identity_key", payload)[0]

    def find_or_create_source(self, item):
        source_hash = hashlib.sha256(json.dumps({
            "source_url": item["url"],
            "source_type": "YOUTUBE",
            "title": item["title"]
        }, sort_keys=True).encode()).hexdigest()

        payload = {
            "source_url": item["url"],
            "source_type": "YOUTUBE",
            "title": item["title"],
            "platform": item.get("platform"),
            "evidence_hash": source_hash,
            "raw_payload": {"mission": "P5.5H"},
            "confidence_score": item.get("confidence_score", 55),
            "validation_status": item.get("validation_status", "provisional")
        }
        return self.req("POST", "/rest/v1/p55a_sources?on_conflict=evidence_hash", payload)[0]

    def find_media_by_url(self, url):
        q = urllib.parse.quote(url, safe="")
        rows = self.req("GET", f"/rest/v1/p55a_media?url=eq.{q}&select=id,animal_id,source_id,url,title,event_name,result,confidence_score,validation_status")
        return rows[0] if rows else None

    def upsert_media(self, item):
        existing = self.find_media_by_url(item["url"])
        if existing:
            return existing

        animal = self.find_animal(item["animal_name"])
        source = self.find_or_create_source(item)

        payload = {
            "animal_id": animal["id"],
            "source_id": source["id"],
            "url": item["url"],
            "platform": item.get("platform"),
            "title": item.get("title"),
            "event_name": item.get("event_name"),
            "result": item.get("result"),
            "bull_score": item.get("bull_score"),
            "rider_score": item.get("rider_score"),
            "ride_time_seconds": item.get("ride_time_seconds"),
            "buckoff": item.get("buckoff"),
            "metadata": {"mission": "P5.5H", "animal_name": item["animal_name"]},
            "confidence_score": item.get("confidence_score", 55),
            "validation_status": item.get("validation_status", "provisional")
        }
        return self.req("POST", "/rest/v1/p55a_media", payload)[0]

    def seed(self):
        return [self.upsert_media(x) for x in MEDIA_EVENT_SEEDS]

    def audit(self, rows):
        return {
            "status": "P5.5H_MEDIA_EVENTS_SEEDED",
            "total": len(rows),
            "unique_urls": len(set(r["url"] for r in rows)),
            "ids": [r["id"] for r in rows]
        }
