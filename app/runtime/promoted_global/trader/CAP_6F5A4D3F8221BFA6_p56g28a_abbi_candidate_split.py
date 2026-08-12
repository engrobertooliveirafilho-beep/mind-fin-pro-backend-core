import json
from pathlib import Path

src = Path("reports/P5.6G27_STRUCTURED_SOURCE_CERTIFICATION/abbi_candidates.json")
rows = json.loads(src.read_text(encoding="utf-8"))

strong = []
facebook = []
generic = []

for r in rows:
    url = r[0] or ""
    title = r[2] or ""

    item = {
        "source_url": url,
        "source_type": r[1],
        "title": title,
        "confidence_score": r[3],
        "validation_status": r[4]
    }

    low = (url + " " + title).lower()

    if "members.americanbuckingbull.com/bulls.aspx?id=" in low:
        item["candidate_type"] = "ABBI_ANIMAL_PROFILE"
        strong.append(item)
    elif "facebook.com/americanbuckingbull" in low and any(x in low for x in ["sire", "son", "daughter", "abbi", "registration"]):
        item["candidate_type"] = "ABBI_SOCIAL_PEDIGREE_SIGNAL"
        facebook.append(item)
    else:
        item["candidate_type"] = "ABBI_GENERIC_OR_WEAK"
        generic.append(item)

out = Path("reports/P5.6G28_ABBI_PEDIGREE_EXTRACTION")
out.mkdir(parents=True, exist_ok=True)

(out / "P56G28A_ABBI_STRONG_PROFILE_CANDIDATES.json").write_text(json.dumps(strong,indent=2,ensure_ascii=False),encoding="utf-8")
(out / "P56G28A_ABBI_SOCIAL_SIGNAL_CANDIDATES.json").write_text(json.dumps(facebook,indent=2,ensure_ascii=False),encoding="utf-8")
(out / "P56G28A_ABBI_GENERIC_REJECTS.json").write_text(json.dumps(generic,indent=2,ensure_ascii=False),encoding="utf-8")

summary = {
    "strong_abbi_profiles": len(strong),
    "abbi_social_signals": len(facebook),
    "generic_or_weak": len(generic),
    "total": len(rows)
}

(out / "P56G28A_ABBI_CANDIDATE_SPLIT_SUMMARY.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

print(json.dumps(summary,indent=2))
