import requests, re, json, hashlib
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G37C_ABBI21_ENTITY_RESOLUTION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

abbi="21"
url=f"http://members.americanbuckingbull.com/bulls.aspx?id={abbi}"

result={
  "mission":MISSION,
  "mode":"FETCH_PARSE_NO_DATABASE_WRITE",
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "abbi":abbi,
  "url":url,
  "status":"UNKNOWN"
}

try:
    r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=60)
    html=r.text
    text=BeautifulSoup(html,"html.parser").get_text(" ",strip=True)

    (out/"21.html").write_text(html,encoding="utf-8")
    (out/"21.txt").write_text(text,encoding="utf-8")

    result["status_code"]=r.status_code
    result["content_length"]=len(html)
    result["sha256"]=hashlib.sha256(html.encode()).hexdigest()

    # tentativa de parse padrão ABBI
    m=re.search(r"Animal Pedigree\s+(.+?)\s+Animal\s+ABBI#\s+(\d+)",text,re.I)
    if m:
        result["official_name"]=m.group(1).strip()
        result["registry_number"]=m.group(2).strip()
        result["status"]="PARSED"
    else:
        result["status"]="FETCHED_PARSE_WEAK"

    # contexto
    idx=text.lower().find("animal pedigree")
    result["context"]=text[idx:idx+800] if idx>=0 else text[:800]

except Exception as e:
    result["status"]="FAILED"
    result["error"]=repr(e)

(out/"P56G37C_ABBI21_ENTITY_RESOLUTION.json").write_text(
 json.dumps(result,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(result,indent=2,ensure_ascii=False))
