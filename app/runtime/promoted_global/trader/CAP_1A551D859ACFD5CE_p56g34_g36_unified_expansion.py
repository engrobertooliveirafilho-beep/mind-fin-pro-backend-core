import os
import re
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup

MISSION="P5.6G34_G36_UNIFIED_EXPANSION"

ROOT=Path(f"reports/{MISSION}")
ROOT.mkdir(parents=True,exist_ok=True)

TARGETS=[
    {
        "animal":"REINDEER MO",
        "abbi":"10010628"
    },
    {
        "animal":"110",
        "abbi":"10007793"
    }
]

session=requests.Session()

RESULT={
    "mission":MISSION,
    "generated_at":datetime.now(timezone.utc).isoformat(),
    "targets":[],
    "summary":{
        "profiles_fetched":0,
        "profiles_failed":0,
        "signals_found":0
    }
}

for target in TARGETS:

    abbi=target["abbi"]

    url=f"http://members.americanbuckingbull.com/bulls.aspx?id={abbi}"

    node={
        "animal":target["animal"],
        "abbi":abbi,
        "url":url,
        "status":"UNKNOWN",
        "pedigree":[],
        "progeny":[],
        "valuation":[],
        "owners":[],
        "breeders":[],
        "competition":[],
        "signals":[]
    }

    try:

        r=session.get(
            url,
            timeout=60,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )

        html=r.text

        html_file=ROOT/f"{abbi}.html"
        html_file.write_text(html,encoding="utf-8")

        text=BeautifulSoup(html,"html.parser").get_text(" ",strip=True)

        txt_file=ROOT/f"{abbi}.txt"
        txt_file.write_text(text,encoding="utf-8")

        node["status"]="FETCHED"

        RESULT["summary"]["profiles_fetched"]+=1

        patterns=[
            r"Sire",
            r"Dam",
            r"GrandSire",
            r"GrandDam",
            r"Owner",
            r"Breeder",
            r"Production",
            r"Competition",
            r"Sale",
            r"Embryo",
            r"Semen",
            r"Offspring"
        ]

        for p in patterns:
            if re.search(p,text,re.I):
                node["signals"].append(p)

        RESULT["summary"]["signals_found"] += len(node["signals"])

        node["sha256"]=hashlib.sha256(
            html.encode()
        ).hexdigest()

    except Exception as e:

        node["status"]="FAILED"
        node["error"]=repr(e)

        RESULT["summary"]["profiles_failed"]+=1

    RESULT["targets"].append(node)

(ROOT/"UNIFIED_EXPANSION_RESULT.json").write_text(
    json.dumps(
        RESULT,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print(
    json.dumps(
        RESULT["summary"],
        indent=2
    )
)

print()
print("OUTPUT =", ROOT)

