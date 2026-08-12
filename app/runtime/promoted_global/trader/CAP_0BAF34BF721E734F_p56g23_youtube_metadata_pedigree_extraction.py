import json, re
from datetime import datetime, timezone

rows=json.load(open("P56G22_YOUTUBE_PEDIGREE_CANDIDATES.json",encoding="utf-8"))

high=[r for r in rows if r.get("status")=="NEEDS_TRANSCRIPT_EXTRACTION"]

records=[]

for r in high:
    text=" ".join([str(r.get("title") or ""), str(r.get("description") or "")])

    sire=None
    dam=None

    sm=re.search(r"(?i)\bsire[:\s]+([A-Z][A-Za-z0-9' .-]{2,50})", text)
    dm=re.search(r"(?i)\bdam[:\s]+([A-Z][A-Za-z0-9' .-]{2,50})", text)

    if sm:
        sire=sm.group(1).strip(" .,-")
    if dm:
        dam=dm.group(1).strip(" .,-")

    records.append({
        "animal":"Smooth Operator",
        "sire":sire,
        "dam":dam,
        "source_url":r["video_url"],
        "source_type":"PBR_PROFILE",
        "confidence":70 if (sire or dam) else 0,
        "video_title":r["title"],
        "status":"STRUCTURED_READY" if (sire or dam) else "NO_EXPLICIT_PEDIGREE_IN_METADATA"
    })

snapshot={
    "mission":"P5.6G23_YOUTUBE_METADATA_PEDIGREE_EXTRACTION",
    "created_at":datetime.now(timezone.utc).isoformat(),
    "input_high_signal":len(high),
    "structured_ready":sum(1 for r in records if r["status"]=="STRUCTURED_READY"),
    "records":records
}

open("P56G23_YOUTUBE_METADATA_PEDIGREE_EXTRACTION.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False))
print(json.dumps(snapshot,indent=2,ensure_ascii=False))
