
import os
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SERPAPI_URL = "https://serpapi.com/search.json"

def serpapi_search(query, limit=5):
    key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_KEY")

    if not key:
        return {
            "query": query,
            "status": "BLOCKED_NO_SERPAPI_KEY",
            "results": []
        }

    params = urllib.parse.urlencode({
        "engine": "google",
        "q": query,
        "api_key": key,
        "num": limit
    })

    url = SERPAPI_URL + "?" + params

    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))

        organic = data.get("organic_results", [])[:limit]

        return {
            "query": query,
            "status": "OK",
            "results": [
                {
                    "title": x.get("title"),
                    "link": x.get("link"),
                    "snippet": x.get("snippet")
                }
                for x in organic
                if x.get("link")
            ]
        }

    except Exception as e:
        msg = repr(e)
        if "429" in msg:
            status = "BLOCKED_RATE_LIMIT_429"
        else:
            status = "ERROR"

        return {
            "query": query,
            "status": status,
            "error": msg,
            "results": []
        }

def run(plan_path="P56G18_AUTOMATED_SOURCE_HARVEST_PLAN.json", sleep_seconds=2):
    plan = json.load(open(plan_path, encoding="utf-8"))
    searched = []

    for item in plan["queries"]:
        res = serpapi_search(item["query"], limit=5)
        res["animal"] = item["animal"]
        res["source_type"] = item["source_type"]
        searched.append(res)
        time.sleep(sleep_seconds)

    candidates = []

    for block in searched:
        for r in block.get("results", []):
            candidates.append({
                "animal": block["animal"],
                "sire": None,
                "dam": None,
                "source_url": r["link"],
                "source_type": block["source_type"],
                "confidence": 0,
                "status": "FOUND_URL_NEEDS_STRUCTURED_PARSE",
                "title": r.get("title"),
                "snippet": r.get("snippet"),
                "query": block["query"]
            })

    snapshot = {
        "mission": "P5.6G20_REAL_WEB_SEARCH_ADAPTER",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "REAL_SEARCH_NO_DB_MUTATION",
        "queries_total": len(plan["queries"]),
        "search_status_counts": {},
        "candidate_urls": len(candidates),
        "outputs": [
            "P56G20_REAL_SEARCH_RESULTS.json",
            "P56G20_REAL_URL_CANDIDATES.json"
        ]
    }

    for s in searched:
        snapshot["search_status_counts"][s["status"]] = snapshot["search_status_counts"].get(s["status"], 0) + 1

    open("P56G20_REAL_SEARCH_RESULTS.json","w",encoding="utf-8").write(
        json.dumps(searched,indent=2,ensure_ascii=False)
    )

    open("P56G20_REAL_URL_CANDIDATES.json","w",encoding="utf-8").write(
        json.dumps(candidates,indent=2,ensure_ascii=False)
    )

    open("P56G20_REAL_WEB_SEARCH_ADAPTER_SNAPSHOT.json","w",encoding="utf-8").write(
        json.dumps(snapshot,indent=2,ensure_ascii=False)
    )

    print(json.dumps(snapshot,indent=2,ensure_ascii=False))

if __name__ == "__main__":
    run()
