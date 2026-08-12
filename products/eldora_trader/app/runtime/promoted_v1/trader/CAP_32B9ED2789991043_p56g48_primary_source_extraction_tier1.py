import requests, json, re, hashlib
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G48_PRIMARY_SOURCE_EXTRACTION_TIER1"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

sources=[
 {
  "kind":"progeny",
  "source_id":"5a852c21-e633-4e5c-876e-f8b0140b2443",
  "title":"Lot #M11 - One IVF Embryo",
  "url":"https://www.thebreedersconnection.com/lotbc_18glcM11.html"
 },
 {
  "kind":"progeny",
  "source_id":"a33fda4e-5550-4810-af67-9119d7d3b4d2",
  "title":"BUCK HIM & BREED HIM!!! Lot #08 - 6X22 Hush Money",
  "url":"https://www.facebook.com/bullpimp/posts/buck-him-breed-himlot-08-6x22-hush-money-3yr-old-son-of-bruiser-out-of-a-bushwac/10163691835468254/"
 },
 {
  "kind":"progeny",
  "source_id":"531ad359-6f20-41e6-94c5-5416d9f33918",
  "title":"Remembering Bushwacker",
  "url":"https://www.agdaily.com/livestock/remembering-bushwacker-world-champion-bull-dies-at-18/"
 },
 {
  "kind":"progeny",
  "source_id":"585a9e9f-7707-4157-8733-703a54140ab6",
  "title":"2 FROZEN EMBRYOS SIRE: Blueberry Wine",
  "url":"https://www.thebreedersconnection.com/lot809.html"
 },
 {
  "kind":"valuation",
  "source_id":"6089c898-96b8-4a53-b0f3-a9cc099a8616",
  "title":"Elite Breeder Sales post",
  "url":"https://www.facebook.com/EliteBreederSales/posts/heres-an-opportunity-you-dont-get-every-day-selling-as-lot-4-is-1-straw-of-bushw/1277348147729241/"
 },
 {
  "kind":"valuation",
  "source_id":"f8895882-34f1-45d5-b923-db023bc65830",
  "title":"Bucking Bull Semen for Sale",
  "url":"https://bonsallbuckingbulls.com/semen-sales/"
 }
]

def clean(x):
    return re.sub(r"\s+"," ",x or "").strip()

def extract_signals(text):
    low=text.lower()
    signals={
      "money":re.findall(r"\$\s?[0-9][0-9,]*(?:\.\d+)?",text),
      "lots":re.findall(r"\bLot\s?#?\s?[A-Za-z0-9\-]+",text,re.I),
      "abbi_numbers":re.findall(r"ABBI#?\s*[:#]?\s*(\d+)",text,re.I),
      "son_of":re.findall(r"([A-Za-z0-9' \-]+?)\s+(?:son of|sired by)\s+([A-Za-z0-9' \-]+)",text,re.I),
      "daughter_of":re.findall(r"([A-Za-z0-9' \-]+?)\s+daughter of\s+([A-Za-z0-9' \-]+)",text,re.I),
      "semen_mentions":"semen" in low,
      "embryo_mentions":"embryo" in low or "embryos" in low,
      "sold_mentions":"sold" in low,
      "auction_mentions":"auction" in low or "sale" in low
    }
    return signals

result={
 "mission":MISSION,
 "mode":"FETCH_EXTRACT_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "sources":[],
 "summary":{},
 "status":"PASS"
}

for i,s in enumerate(sources,1):
    rec={**s,"status":"UNKNOWN"}
    try:
        r=requests.get(s["url"],headers={"User-Agent":"Mozilla/5.0"},timeout=60)
        html=r.text or ""
        text=clean(BeautifulSoup(html,"html.parser").get_text(" ",strip=True))

        (out/f"{i}_{s['kind']}.html").write_text(html,encoding="utf-8",errors="ignore")
        (out/f"{i}_{s['kind']}.txt").write_text(text,encoding="utf-8",errors="ignore")

        rec.update({
          "status":"FETCHED",
          "status_code":r.status_code,
          "final_url":r.url,
          "content_length":len(text),
          "sha256":hashlib.sha256(html.encode(errors='ignore')).hexdigest(),
          "signals":extract_signals(text),
          "preview":text[:1500]
        })

    except Exception as e:
        rec["status"]="FAILED"
        rec["error"]=repr(e)

    result["sources"].append(rec)

result["summary"]={
 "sources_total":len(sources),
 "fetched":sum(1 for x in result["sources"] if x["status"]=="FETCHED"),
 "failed":sum(1 for x in result["sources"] if x["status"]=="FAILED"),
 "with_money":sum(1 for x in result["sources"] if x.get("signals",{}).get("money")),
 "with_abbi":sum(1 for x in result["sources"] if x.get("signals",{}).get("abbi_numbers")),
 "with_embryo":sum(1 for x in result["sources"] if x.get("signals",{}).get("embryo_mentions")),
 "with_semen":sum(1 for x in result["sources"] if x.get("signals",{}).get("semen_mentions"))
}

(out/"P56G48_PRIMARY_SOURCE_EXTRACTION_TIER1.json").write_text(
 json.dumps(result,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(result["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)
