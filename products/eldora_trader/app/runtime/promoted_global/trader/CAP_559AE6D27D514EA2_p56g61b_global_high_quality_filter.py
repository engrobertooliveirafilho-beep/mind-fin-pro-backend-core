import json,re
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G61B_GLOBAL_HIGH_QUALITY_SOURCE_FILTER"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

src=Path("reports/P5.6G61A_GLOBAL_BUCKING_GENETICS_SOURCE_CENSUS/P56G61A_GLOBAL_SOURCE_CENSUS.json")
data=json.loads(src.read_text(encoding="utf-8"))

ALLOW_DOMAINS=[
 "members.americanbuckingbull.com",
 "americanbuckingbull.com",
 "pbr.com",
 "thebreedersconnection.com",
 "bonsallbuckingbulls.com",
 "buckingstocktalk.com",
 "bennybinionsale.com",
 "shippyrodeobulls.com",
 "strategycattle.com"
]

BLOCK_DOMAINS=[
 "google.com",
 "youtube.com",
 "instagram.com",
 "etsy.com"
]

high=[]
review=[]
noise=[]

def domain(url):
    if not url: return ""
    return re.sub(r"^www\.","",re.sub(r"^https?://","",url).split("/")[0].lower())

for s in data["top_signal_sources"]:
    d=domain(s.get("source_url"))

    if d in BLOCK_DOMAINS:
        noise.append({**s,"domain":d,"reason":"BLOCKED_DOMAIN"})
        continue

    if d in ALLOW_DOMAINS:
        high.append({**s,"domain":d,"reason":"ALLOW_DOMAIN"})
        continue

    if s.get("hit_count",0) >= 4:
        review.append({**s,"domain":d,"reason":"HIGH_SIGNAL_UNKNOWN_DOMAIN"})
    else:
        noise.append({**s,"domain":d,"reason":"LOW_SIGNAL_OR_UNKNOWN_DOMAIN"})

report={
 "mission":MISSION,
 "mode":"FILTER_ONLY_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":{
   "input_sources":len(data["top_signal_sources"]),
   "high_quality":len(high),
   "review":len(review),
   "noise":len(noise)
 },
 "high_quality_sources":high,
 "review_sources":review,
 "noise_sources":noise,
 "status":"PASS"
}

(out/"P56G61B_GLOBAL_HIGH_QUALITY_SOURCE_FILTER.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(report["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)
