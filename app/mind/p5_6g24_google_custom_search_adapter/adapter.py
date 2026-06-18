
import os, json, time, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone

URL = "https://www.googleapis.com/customsearch/v1"

def google_cse_search(query, num=5):
    key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CSE_ID")

    if not key or not cx:
        return {"query": query, "status": "BLOCKED_MISSING_GOOGLE_API_KEY_OR_CSE_ID", "results": []}

    params = urllib.parse.urlencode({
        "key": key,
        "cx": cx,
        "q": query,
        "num": num
    })

    try:
        with urllib.request.urlopen(URL + "?" + params, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))

        return {
            "query": query,
            "status": "OK",
            "results": [
                {
                    "title": x.get("title"),
                    "link": x.get("link"),
                    "snippet": x.get("snippet"),
                    "displayLink": x.get("displayLink")
                }
                for x in data.get("items", [])
                if x.get("link")
            ]
        }

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return {"query": query, "status": f"HTTP_{e.code}", "error": body, "results": []}
    except Exception as e:
        return {"query": query, "status": "ERROR", "error": repr(e), "results": []}

def run(plan_path="P56G18_AUTOMATED_SOURCE_HARVEST_PLAN.json", sleep_seconds=1):
    plan = json.load(open(plan_path, encoding="utf-8"))
    searched = []

    for q in plan["queries"]:
        res = google_cse_search(q["query"], num=5)
        res["animal"] = q["animal"]
        res["source_type"] = q["source_type"]
        searched.append(res)
        time.sleep(sleep_seconds)

    candidates = []
    for block in searched:
        for r in block.get("results", []):
            text = " ".join([str(r.get("title") or ""), str(r.get("snippet") or "")]).lower()
            animal_match = block["animal"].lower() in text
            pedigree_signal = any(x in text for x in ["sire", "dam", "pedigree", "breeding", "offspring"])

            candidates.append({
                "animal": block["animal"],
                "sire": None,
                "dam": None,
                "source_url": r["link"],
                "source_type": block["source_type"],
                "confidence": 0,
                "title": r.get("title"),
                "snippet": r.get("snippet"),
                "displayLink": r.get("displayLink"),
                "query": block["query"],
                "animal_match": animal_match,
                "pedigree_signal": pedigree_signal,
                "status": "NEEDS_STRUCTURED_PARSE" if animal_match and pedigree_signal else "LOW_SIGNAL"
            })

    snapshot = {
        "mission": "P5.6G24_GOOGLE_CUSTOM_SEARCH_ADAPTER",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "REAL_GOOGLE_CSE_NO_DB_MUTATION",
        "queries_total": len(plan["queries"]),
        "status_counts": {},
        "candidate_urls": len(candidates),
        "structured_parse_candidates": sum(1 for c in candidates if c["status"] == "NEEDS_STRUCTURED_PARSE"),
        "outputs": [
            "P56G24_GOOGLE_CSE_RESULTS.json",
            "P56G24_GOOGLE_CSE_CANDIDATES.json"
        ]
    }

    for s in searched:
        snapshot["status_counts"][s["status"]] = snapshot["status_counts"].get(s["status"], 0) + 1

    open("P56G24_GOOGLE_CSE_RESULTS.json","w",encoding="utf-8").write(json.dumps(searched,indent=2,ensure_ascii=False))
    open("P56G24_GOOGLE_CSE_CANDIDATES.json","w",encoding="utf-8").write(json.dumps(candidates,indent=2,ensure_ascii=False))
    open("P56G24_GOOGLE_CSE_SNAPSHOT.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False))

    print(json.dumps(snapshot,indent=2,ensure_ascii=False))

if __name__ == "__main__":
    run()
