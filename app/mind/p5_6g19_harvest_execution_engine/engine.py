
import json
import re
import urllib.parse
from datetime import datetime, timezone
from app.mind.p5_6g15_structured_pedigree_source_connector import StructuredPedigreeSourceConnector

def classify_url(url):
    u = (url or "").lower()
    if "theabbi" in u:
        return "ABBI_PROFILE"
    if "pbr.com" in u:
        return "PBR_PROFILE"
    if "sale" in u or "catalog" in u or "lot" in u:
        return "SALE_CATALOG"
    if "semen" in u:
        return "SEMEN_CATALOG"
    if "embryo" in u:
        return "EMBRYO_CATALOG"
    if "breeder" in u or "registry" in u:
        return "BREEDER_REGISTRY"
    return None

def fake_search_url(query):
    # Placeholder seguro: não usa Google/SerpAPI; gera URL-alvo para execução futura real.
    return "SEARCH_REQUIRED://" + urllib.parse.quote(query)

def build_candidates(plan_path="P56G18_AUTOMATED_SOURCE_HARVEST_PLAN.json"):
    plan = json.load(open(plan_path, encoding="utf-8"))
    candidates = []

    for q in plan["queries"]:
        source_url = fake_search_url(q["query"])
        candidates.append({
            "animal": q["animal"],
            "sire": None,
            "dam": None,
            "source_url": source_url,
            "source_type": q["source_type"],
            "confidence": 0,
            "status": "SEARCH_REQUIRED",
            "query": q["query"]
        })

    return candidates

def run():
    candidates = build_candidates()
    connector = StructuredPedigreeSourceConnector()

    structured_ready = [
        c for c in candidates
        if c.get("sire") or c.get("dam")
    ]

    result = connector.run_batch(structured_ready) if structured_ready else {
        "status": "NO_STRUCTURED_RECORDS_READY",
        "accepted": 0,
        "rejected": 0,
        "accepted_items": [],
        "rejected_items": []
    }

    snapshot = {
        "mission": "P5.6G19_HARVEST_EXECUTION_ENGINE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "EXECUTOR_CREATED_NO_WEB_NO_DB_MUTATION",
        "planned_candidates": len(candidates),
        "structured_ready": len(structured_ready),
        "connector_result": result,
        "candidates_file": "P56G19_HARVEST_CANDIDATES.json",
        "next_required": "Replace SEARCH_REQUIRED urls with real ABBI/PBR/catalog URLs and explicit sire/dam fields."
    }

    open("P56G19_HARVEST_CANDIDATES.json","w",encoding="utf-8").write(
        json.dumps(candidates,indent=2,ensure_ascii=False)
    )
    open("P56G19_HARVEST_EXECUTION_SNAPSHOT.json","w",encoding="utf-8").write(
        json.dumps(snapshot,indent=2,ensure_ascii=False)
    )

    print(json.dumps(snapshot,indent=2,ensure_ascii=False))

if __name__ == "__main__":
    run()
