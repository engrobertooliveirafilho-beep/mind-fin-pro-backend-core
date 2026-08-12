import os, json, datetime, traceback, requests, time
from app.mind.p5_5s_source_expansion_autopilot.autopilot import SourceExpansionAutopilot
from app.mind.p5_5t_real_fetcher_search_connector.connector import RealFetcherSearchConnector
from app.mind.p5_6f1_animal_discovery_engine.engine import AnimalDiscoveryEngine
from app.mind.p5_6b4_youtube_acquisition_engine.engine import YouTubeAcquisitionEngine
from app.mind.p5_6b5_judge_real_biomechanics_binder.binder import JudgeRealBiomechanicsBinder
from app.mind.p5_6b6_real_valuation_binder.binder import RealValuationBinder
from app.mind.p5_6c_pedigree_source_validation.validator import PedigreeSourceValidator
from app.mind.p5_6d_market_valuation_real_prices.prices import MarketValuationRealPrices
from app.mind.p5_5x_genetic_graph_builder.graph import GeneticGraphBuilder
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Prefer":"count=exact"}

tables=["p55a_animals","p55a_sources","p55a_media","p55a_biomechanics","p55a_judge_scores","p55a_valuation_events","p55a_reproduction_records","p55a_pedigree_edges","p55a_country_rankings","p55a_audit_logs"]

def count(t):
    r=requests.get(f"{u}/rest/v1/{t}?select=id&limit=1",headers=h)
    return int((r.headers.get("content-range") or "0-0/0").split("/")[-1])

def safe(name, fn):
    try:
        return {"ok":True,"name":name,"result":fn()}
    except Exception as e:
        return {"ok":False,"name":name,"error":str(e),"trace":traceback.format_exc()[-1500:]}

before={t:count(t) for t in tables}
results={}

results["source_expansion"]=safe("source_expansion",lambda:SourceExpansionAutopilot().run_once(100))

fetch=[]
for i in range(2):
    fetch.append(safe(f"fetch_{i+1}",lambda:RealFetcherSearchConnector().run_once(10)))
    time.sleep(6)
results["fetch"]=fetch

results["animal_discovery_audit_only"]=safe("animal_discovery",lambda:AnimalDiscoveryEngine().run_once(2600,4))
results["youtube_acquisition"]=safe("youtube_acquisition",lambda:YouTubeAcquisitionEngine().run_once(25))
results["judge_binder"]=safe("judge_binder",lambda:JudgeRealBiomechanicsBinder().run_once(1000))
results["market_prices"]=safe("market_prices",lambda:MarketValuationRealPrices().run_once())
results["pedigree_validation"]=safe("pedigree_validation",lambda:PedigreeSourceValidator().run_once())
results["real_valuation"]=safe("real_valuation",lambda:RealValuationBinder().run_once())
results["genetic_graph"]=safe("genetic_graph",lambda:GeneticGraphBuilder().run_once())

after={t:count(t) for t in tables}
snap=ExecutiveSnapshot().build()

audit={
    "mission":"P5_6_FULL_STRUCTURAL_EXPANSION_RUNTIME",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "before":before,
    "after":after,
    "growth":{t:after[t]-before[t] for t in tables},
    "results":results,
    "snapshot":snap
}

open("p56_full_structural_expansion_runtime_audit.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2,default=str))

print(json.dumps({
    "mission":audit["mission"],
    "before":before,
    "after":after,
    "growth":audit["growth"],
    "top_candidates":results["animal_discovery_audit_only"].get("result",{}).get("top_candidates",[])[:10] if results["animal_discovery_audit_only"].get("ok") else [],
    "critical_gaps":snap.get("critical_gaps"),
    "audit_file":"p56_full_structural_expansion_runtime_audit.json"
},indent=2,ensure_ascii=False,default=str))
