import json,re,hashlib,requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G62B_FETCH_66_ABBI_PROFILES"
out=Path(f"reports/{MISSION}")
html_dir=out/"html"
txt_dir=out/"txt"
html_dir.mkdir(parents=True,exist_ok=True)
txt_dir.mkdir(parents=True,exist_ok=True)

src=Path("reports/P5.6G62A_ABBI_MASS_PROFILE_EXPANSION_PLAN/P56G62A_ABBI_MASS_PROFILE_EXPANSION_PLAN.json")
data=json.loads(src.read_text(encoding="utf-8"))

results=[]

def clean(x):
    return re.sub(r"\s+"," ",x or "").strip()

for item in data["missing"]:
    reg=item["registry_number"]
    url=item["url"]

    rec={"registry_number":reg,"url":url,"status":"UNKNOWN"}

    try:
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=45)
        html=r.text or ""
        text=clean(BeautifulSoup(html,"html.parser").get_text(" ",strip=True))

        (html_dir/f"{reg}.html").write_text(html,encoding="utf-8",errors="ignore")
        (txt_dir/f"{reg}.txt").write_text(text,encoding="utf-8",errors="ignore")

        rec.update({
          "status":"FETCHED",
          "status_code":r.status_code,
          "final_url":r.url,
          "content_length":len(text),
          "sha256":hashlib.sha256(html.encode(errors="ignore")).hexdigest()
        })

    except Exception as e:
        rec.update({"status":"FAILED","error":repr(e)})

    results.append(rec)

report={
 "mission":MISSION,
 "mode":"FETCH_ONLY_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":{
   "profiles_total":len(results),
   "profiles_fetched":sum(1 for r in results if r["status"]=="FETCHED"),
   "profiles_failed":sum(1 for r in results if r["status"]=="FAILED"),
   "total_text_length":sum(r.get("content_length",0) for r in results)
 },
 "results":results,
 "status":"PASS"
}

(out/"P56G62B_FETCH_66_ABBI_PROFILES.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(report["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)
