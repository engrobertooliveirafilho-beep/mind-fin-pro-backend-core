import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timezone

src = Path("reports/P5.6G28_ABBI_PEDIGREE_EXTRACTION/P56G28A_ABBI_STRONG_PROFILE_CANDIDATES.json")
rows = json.loads(src.read_text(encoding="utf-8"))

urls = sorted(set(r["source_url"] for r in rows))

out = Path("reports/P5.6G28_ABBI_PEDIGREE_EXTRACTION/fetched_profiles")
out.mkdir(parents=True, exist_ok=True)

ledger = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

for url in urls:
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        body = resp.text or ""
        h = hashlib.sha256(body.encode("utf-8", errors="ignore")).hexdigest()

        fname = url.split("id=")[-1] + ".html"
        (out / fname).write_text(body, encoding="utf-8", errors="ignore")

        ledger.append({
            "source_url": url,
            "status_code": resp.status_code,
            "final_url": resp.url,
            "content_length": len(body),
            "sha256": h,
            "html_file": str(out / fname),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "FETCHED" if resp.status_code == 200 and len(body) > 100 else "WEAK_OR_BLOCKED"
        })

    except Exception as e:
        ledger.append({
            "source_url": url,
            "status": "FETCH_ERROR",
            "error": repr(e),
            "fetched_at": datetime.now(timezone.utc).isoformat()
        })

Path("reports/P5.6G28_ABBI_PEDIGREE_EXTRACTION/P56G28B_FETCH_LEDGER.json").write_text(
    json.dumps(ledger, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(ledger, indent=2, ensure_ascii=False))
