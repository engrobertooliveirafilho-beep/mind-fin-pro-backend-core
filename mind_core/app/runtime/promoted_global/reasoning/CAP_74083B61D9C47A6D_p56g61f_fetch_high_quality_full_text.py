import json,re,hashlib,requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G61F_FETCH_HIGH_QUALITY_FULL_TEXT"
out=Path(f"reports/{MISSION}")
html_dir=out/"html"
txt_dir=out/"txt"
html_dir.mkdir(parents=True,exist_ok=True)
txt_dir.mkdir(parents=True,exist_ok=True)

src=Path("reports/P5.6G61B_GLOBAL_HIGH_QUALITY_SOURCE_FILTER/P56G61B_GLOBAL_HIGH_QUALITY_SOURCE_FILTER.json")
data=json.loads(src.read_text(encoding="utf-8"))

sources=data["high_quality_sources"][:111]

results=[]

def clean(x):
    return re.sub(r"\s+"," ",x or "").strip()

for i,s in enumerate(sources,1):
    url=s.get("source_url")
    rec={**s,"fetch_status":"UNKNOWN"}

    try:
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=45)
        html=r.text or ""
        text=clean(BeautifulSoup(html,"html.parser").get_text(" ",strip=True))

        safe=f"{i:03d}_{hashlib.sha1(url.encode()).hexdigest()[:10]}"
        (html_dir/f"{safe}.html").write_text(html,encoding="utf-8",errors="ignore")
        (txt_dir/f"{safe}.txt").write_text(text,encoding="utf-8",errors="ignore")

        rec.update({
          "fetch_status":"FETCHED",
          "status_code":r.status_code,
          "final_url":r.url,
          "text_length":len(text),
          "sha256":hashlib.sha256(html.encode(errors="ignore")).hexdigest(),
          "html_file":str(html_dir/f"{safe}.html"),
          "txt_file":str(txt_dir/f"{safe}.txt"),
          "preview":text[:800]
        })

    except Exception as e:
        rec.update({
          "fetch_status":"FAILED",
          "error":repr(e)
        })

    results.append(rec)

summary={
 "sources_attempted":len(results),
 "fetched":sum(1 for r in results if r["fetch_status"]=="FETCHED"),
 "failed":sum(1 for r in results if r["fetch_status"]=="FAILED"),
 "total_text_length":sum(r.get("text_length",0) for r in results)
}

report={
 "mission":MISSION,
 "mode":"FETCH_FULL_TEXT_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":summary,
 "results":results,
 "status":"PASS"
}

(out/"P56G61F_FETCH_HIGH_QUALITY_FULL_TEXT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(summary,indent=2,ensure_ascii=False))
print("OUTPUT =",out)
