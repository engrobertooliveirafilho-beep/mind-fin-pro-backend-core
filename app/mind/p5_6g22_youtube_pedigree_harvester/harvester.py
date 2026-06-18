
import os, json, urllib.parse, urllib.request
from datetime import datetime, timezone

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

TARGETS = [
  "Bushwacker bucking bull pedigree sire dam",
  "Bodacious bucking bull pedigree sire dam",
  "SweetPro's Bruiser bucking bull pedigree sire dam",
  "Woopaa bucking bull pedigree sire dam",
  "Little Yellow Jacket bucking bull pedigree sire dam",
  "Long John bucking bull pedigree sire dam",
  "Air Time bucking bull pedigree sire dam",
  "Smooth Operator bucking bull pedigree sire dam"
]

def youtube_search(query, max_results=10):
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        return {"query": query, "status": "BLOCKED_NO_YOUTUBE_API_KEY", "results": []}

    params = urllib.parse.urlencode({
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": key
    })

    url = YOUTUBE_SEARCH_URL + "?" + params

    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))

        results = []
        for item in data.get("items", []):
            vid = item.get("id", {}).get("videoId")
            snip = item.get("snippet", {})
            if not vid:
                continue
            results.append({
                "video_id": vid,
                "video_url": "https://www.youtube.com/watch?v=" + vid,
                "title": snip.get("title"),
                "description": snip.get("description"),
                "channel_title": snip.get("channelTitle"),
                "published_at": snip.get("publishedAt")
            })

        return {"query": query, "status": "OK", "results": results}

    except Exception as e:
        return {"query": query, "status": "ERROR", "error": repr(e), "results": []}

def run():
    blocks = [youtube_search(q) for q in TARGETS]

    candidates = []
    for block in blocks:
        for r in block["results"]:
            text = " ".join([
                str(r.get("title") or ""),
                str(r.get("description") or "")
            ]).lower()

            query_animal = block["query"].split(" bucking bull")[0].lower()
            hard_negative = any(x in text for x in ["pitbull", "doglover", "audiobook", "textile", "worm gear", "oil seal"])
            animal_match = query_animal in text
            domain_match = any(x in text for x in ["bucking", "bull", "pbr", "abbi", "rodeo", "prca"])
            
            score = 0
            if animal_match: score += 40
            if domain_match: score += 20
            if "sire" in text: score += 25
            if "dam" in text: score += 25
            if "pedigree" in text: score += 20
            if "abbi" in text: score += 10
            if "pbr" in text: score += 10
            if hard_negative: score = 0

            status = "NEEDS_TRANSCRIPT_EXTRACTION" if (score >= 70 and animal_match and domain_match and not hard_negative) else "LOW_SIGNAL"

            candidates.append({
                **r,
                "query": block["query"],
                "animal_match": animal_match,
                "domain_match": domain_match,
                "hard_negative": hard_negative,
                "pedigree_signal_score": score,
                "status": status
            })

    snapshot = {
        "mission": "P5.6G22_YOUTUBE_PEDIGREE_HARVESTER",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "YOUTUBE_SEARCH_NO_DB_MUTATION",
        "queries": len(TARGETS),
        "status_counts": {},
        "videos_found": len(candidates),
        "high_signal_candidates": len([c for c in candidates if c["status"] == "NEEDS_TRANSCRIPT_EXTRACTION"]),
        "outputs": [
            "P56G22_YOUTUBE_SEARCH_RESULTS.json",
            "P56G22_YOUTUBE_PEDIGREE_CANDIDATES.json"
        ]
    }

    for b in blocks:
        snapshot["status_counts"][b["status"]] = snapshot["status_counts"].get(b["status"], 0) + 1

    open("P56G22_YOUTUBE_SEARCH_RESULTS.json","w",encoding="utf-8").write(json.dumps(blocks,indent=2,ensure_ascii=False))
    open("P56G22_YOUTUBE_PEDIGREE_CANDIDATES.json","w",encoding="utf-8").write(json.dumps(candidates,indent=2,ensure_ascii=False))
    open("P56G22_YOUTUBE_PEDIGREE_HARVESTER_SNAPSHOT.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False))

    print(json.dumps(snapshot,indent=2,ensure_ascii=False))

if __name__ == "__main__":
    run()
