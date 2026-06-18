from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse
import hashlib, json, re

PRIORITY_SOURCES = [
 "ABBI","PBR","PBR_BRASIL","PRCA","NFR","CBR","AUCTION","GENETIC_CATALOG",
 "YOUTUBE","FACEBOOK","INSTAGRAM","TIKTOK","BREEDER_SITE","COMPANY_SITE",
 "ARTICLE","JOURNAL","MAGAZINE","PODCAST","HISTORIC_VIDEO","ACADEMIC","VETERINARY"
]

SEED_QUERIES = [
 "site:pbr.com bull Bushwacker pedigree",
 "site:pbr.com bull Woopaa score",
 "site:americanbuckingbull.com ABBI bull pedigree",
 "site:prorodeo.com NFR bucking bull",
 "site:youtube.com PBR bull ride official score",
 "site:pbrbrazil.com.br touro rodeio nota",
 "leilão genética touro rodeio sêmen",
 "catálogo genética bucking bull"
]

def now(): return datetime.now(timezone.utc).isoformat()

def sha(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()

def domain(url):
    try: return urlparse(url).netloc.lower().replace("www.","")
    except Exception: return ""

def normalize_text(x):
    return re.sub(r"\s+"," ",str(x or "").strip())

@dataclass
class WebEvidence:
    url: str
    source_type: str
    title: str = ""
    snippet: str = ""
    discovered_by: str = "p55b"
    captured_at: str = field(default_factory=now)

    def record(self):
        payload = self.__dict__.copy()
        payload["domain"] = domain(self.url)
        payload["evidence_hash"] = sha(payload)
        payload["confidence_score"] = self.score()
        payload["validation_status"] = self.band(payload["confidence_score"])
        return payload

    def score(self):
        d = domain(self.url)
        score = 30
        if any(x in d for x in ["pbr","prorodeo","americanbuckingbull","nfrexperience"]): score += 35
        if self.title: score += 10
        if self.snippet: score += 10
        if self.source_type in PRIORITY_SOURCES: score += 10
        return min(100, score)

    def band(self, score):
        if score < 40: return "rejected"
        if score < 60: return "weak"
        if score < 75: return "provisional"
        if score < 90: return "reliable"
        return "highly_reliable"

class BullWebAbsorptionEngine:
    def seed_queue(self):
        return [{"query":q,"priority":100-i,"status":"pending","created_at":now()} for i,q in enumerate(SEED_QUERIES)]

    def normalize_result(self, item):
        return WebEvidence(
            url=item.get("url") or item.get("source_url") or "",
            source_type=item.get("source_type","OTHER"),
            title=normalize_text(item.get("title","")),
            snippet=normalize_text(item.get("snippet",""))
        ).record()

    def dedupe(self, records):
        seen, out = set(), []
        for r in records:
            key = r.get("evidence_hash") or sha(r)
            if key not in seen:
                seen.add(key); out.append(r)
        return out

    def extract_candidate_animal_claims(self, text):
        text = normalize_text(text)
        patterns = {
            "possible_registry_number": r"\b\d{1,3}[/.-]\d{1,3}\b",
            "possible_year": r"\b(19[7-9]\d|20[0-3]\d)\b",
            "possible_score": r"\b([4-9]\d(?:\.\d+)?)\b"
        }
        return {k: re.findall(v,text) for k,v in patterns.items()}

    def audit_batch(self, records):
        total=len(records); reliable=sum(1 for r in records if r.get("confidence_score",0)>=75)
        return {"status":"P5.5B_BATCH_AUDITED","total":total,"reliable_or_better":reliable,"created_at":now()}
