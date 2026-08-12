import os, json, datetime, traceback, requests, time
from app.mind.p5_5s_source_expansion_autopilot.autopilot import SourceExpansionAutopilot
from app.mind.p5_5t_real_fetcher_search_connector.connector import RealFetcherSearchConnector
from app.mind.p5_6f1_animal_discovery_engine.engine import AnimalDiscoveryEngine
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Prefer":"count=exact"}

def count(t):
    r=requests.get(f"{u}/rest/v1/{t}?select=id&limit=1",headers=h)
    return int((r.headers.get("content-range") or "0-0/0").split("/")[-1])

def safe(fn):
    try: return {"ok":True,"result":fn()}
    except Exception as e: return {"ok":False,"error":str(e),"trace":traceback.format_exc()[-1500:]}

before={t:count(t) for t in ["p55a_animals","p55a_sources","p55a_media","p55a_reproduction_records","p55a_valuation_events","p55a_audit_logs"]}

results={}
results["source_expansion"]=safe(lambda:SourceExpansionAutopilot().run_once(100))
fetch_runs=[]
for i in range(1,4):
    fetch_runs.append(safe(lambda:RealFetcherSearchConnector().run_once(15)))
    time.sleep(5)
results["fetch_runs"]=fetch_runs
results["animal_discovery_audit_only"]=safe(lambda:AnimalDiscoveryEngine().run_once(2600,3))

after={t:count(t) for t in before}
snap=ExecutiveSnapshot().build()

audit={
    "mission":"P5_6_MASTER_DISCOVERY_EXPANSION_AUDIT_ONLY",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "before":before,
    "after":after,
    "growth":{t:after[t]-before[t] for t in before},
    "results":results,
    "snapshot":snap
}

open("p56_master_discovery_expansion_audit_only.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2,default=str))

print(json.dumps({
    "mission":audit["mission"],
    "before":before,
    "after":after,
    "growth":audit["growth"],
    "top_candidates":results["animal_discovery_audit_only"].get("result",{}).get("top_candidates",[])[:10],
    "critical_gaps":snap.get("critical_gaps"),
    "audit_file":"p56_master_discovery_expansion_audit_only.json"
},indent=2,ensure_ascii=False,default=str))
