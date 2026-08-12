import re, json
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G40_ABBI_STRUCTURAL_PEDIGREE_PARSER"
src=Path("reports/P5.6G39_ABBI_MAX_GENETIC_EXPANSION_BFS")
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

def clean(x):
    return re.sub(r"\s+"," ",x or "").strip()

def parse_context(text):
    low=text.lower()
    start=low.find("animal pedigree")
    end=low.find("phone:")
    ctx=text[start:end if end!=-1 else len(text)] if start!=-1 else text[:1500]
    return clean(ctx)

def parse_profile(ctx):
    result={
      "animal":None,
      "abbi":None,
      "sire":None,
      "sire_abbi":None,
      "dam":None,
      "dam_abbi":None,
      "status":"UNKNOWN",
      "warnings":[]
    }

    m=re.search(r"Animal Pedigree\s+(.+?)\s+Animal\s+ABBI#\s+(\d+)",ctx,re.I)
    if not m:
        result["status"]="PARSE_FAILED_HEADER"
        return result

    result["animal"]=clean(m.group(1))
    result["abbi"]=clean(m.group(2))

    after=ctx[m.end():]

    # bloco entre "!" e "Sire Dam ABBI#"
    b=re.search(r"!\s+(.+?)\s+Sire\s+Dam\s+ABBI#\s+(.+?)(?:Sire Side:|Dam Side:|$)",after,re.I)
    if not b:
        result["status"]="PARSE_FAILED_PARENT_BLOCK"
        return result

    names_block=clean(b.group(1))
    abbi_block=clean(b.group(2))

    nums=re.findall(r"\d+",abbi_block)

    if len(nums)==0:
        result["status"]="NO_PARENT_ABBI"
        return result

    if len(nums)==1:
        result["sire"]=names_block
        result["sire_abbi"]=nums[0]
        result["status"]="PARTIAL_ONLY_SIRE"
        result["warnings"].append("Only one parent ABBI number found")
        return result

    sire_abbi=nums[0]
    dam_abbi=nums[1]
    result["sire_abbi"]=sire_abbi
    result["dam_abbi"]=dam_abbi

    # estratégia estrutural: buscar perfis dos pais no mesmo lote para resolver nomes por ABBI
    result["raw_names_block"]=names_block
    result["status"]="PARENT_ABBI_EXTRACTED"

    return result

# primeira passagem: parse header dos HTMLs para mapear ABBI -> nome oficial
profiles={}
for html_file in src.glob("*.html"):
    html=html_file.read_text(encoding="utf-8",errors="ignore")
    text=clean(BeautifulSoup(html,"html.parser").get_text(" ",strip=True))
    ctx=parse_context(text)
    parsed=parse_profile(ctx)
    parsed["source_file"]=str(html_file)
    parsed["source_url"]=f"http://members.americanbuckingbull.com/bulls.aspx?id={html_file.stem}"
    parsed["context"]=ctx
    profiles[html_file.stem]=parsed

abbi_to_name={}
for abbi,p in profiles.items():
    if p.get("animal") and p.get("abbi"):
        abbi_to_name[p["abbi"]]=p["animal"]

# segunda passagem: resolver sire/dam por ABBI quando possível
edge_candidates=[]
blocked=[]

for abbi,p in profiles.items():
    if not p.get("animal") or not p.get("abbi"):
        blocked.append({"profile":abbi,"reason":"HEADER_PARSE_FAILED","profile_status":p.get("status")})
        continue

    if p.get("sire_abbi"):
        sire_name=abbi_to_name.get(p["sire_abbi"])
        if sire_name:
            p["sire"]=sire_name
            edge_candidates.append({
              "parent":sire_name,
              "parent_abbi":p["sire_abbi"],
              "child":p["animal"],
              "child_abbi":p["abbi"],
              "relation":"sire",
              "confidence_score":90,
              "status":"STRUCTURAL_CANDIDATE"
            })
        else:
            blocked.append({
              "child":p["animal"],
              "child_abbi":p["abbi"],
              "relation":"sire",
              "parent_abbi":p["sire_abbi"],
              "reason":"PARENT_PROFILE_NOT_IN_BATCH"
            })

    if p.get("dam_abbi"):
        dam_name=abbi_to_name.get(p["dam_abbi"])
        if dam_name:
            p["dam"]=dam_name
            edge_candidates.append({
              "parent":dam_name,
              "parent_abbi":p["dam_abbi"],
              "child":p["animal"],
              "child_abbi":p["abbi"],
              "relation":"dam",
              "confidence_score":90,
              "status":"STRUCTURAL_CANDIDATE"
            })
        else:
            blocked.append({
              "child":p["animal"],
              "child_abbi":p["abbi"],
              "relation":"dam",
              "parent_abbi":p["dam_abbi"],
              "reason":"PARENT_PROFILE_NOT_IN_BATCH"
            })

result={
  "mission":MISSION,
  "mode":"STRUCTURAL_PARSE_NO_DATABASE_WRITE",
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "summary":{
    "profiles_parsed":len(profiles),
    "abbi_name_map":len(abbi_to_name),
    "edge_candidates":len(edge_candidates),
    "blocked":len(blocked)
  },
  "abbi_to_name":abbi_to_name,
  "profiles":profiles,
  "edge_candidates":edge_candidates,
  "blocked":blocked,
  "status":"PASS"
}

(out/"P56G40_ABBI_STRUCTURAL_PEDIGREE_PARSE.json").write_text(
  json.dumps(result,indent=2,ensure_ascii=False),
  encoding="utf-8"
)

print(json.dumps(result["summary"],indent=2,ensure_ascii=False))
print()
for e in edge_candidates:
    print(e["parent"],"->",e["child"],e["relation"],e["confidence_score"])

print()
print("BLOCKED =", len(blocked))
