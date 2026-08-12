import os, json, datetime, traceback, requests

from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot
from app.mind.p5_6b4_youtube_acquisition_engine.engine import YouTubeAcquisitionEngine
from app.mind.p5_6b5_judge_real_biomechanics_binder.binder import JudgeRealBiomechanicsBinder
from app.mind.p5_6b6_real_valuation_binder.binder import RealValuationBinder
from app.mind.p5_6c_pedigree_source_validation.validator import PedigreeSourceValidator
from app.mind.p5_6d_market_valuation_real_prices.prices import MarketValuationRealPrices
from app.mind.p5_5x_genetic_graph_builder.graph import GeneticGraphBuilder

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Prefer":"count=exact"}

def count(t):
    r=requests.get(f"{u}/rest/v1/{t}?select=id&limit=1",headers=h)
    return int((r.headers.get("content-range") or "0-0/0").split("/")[-1])

def safe(name, fn):
    try:
        return {"ok":True,"result":fn()}
    except Exception as e:
        return {"ok":False,"error":str(e),"trace":traceback.format_exc()[-2000:]}

tables=["p55a_animals","p55a_sources","p55a_media","p55a_biomechanics","p55a_judge_scores","p55a_valuation_events","p55a_reproduction_records","p55a_country_rankings","p55a_audit_logs"]
before={t:count(t) for t in tables}

results={}
results["B4_youtube_cycle_1"]=safe("B4",lambda:YouTubeAcquisitionEngine().run_once(20))
results["B4_youtube_cycle_2"]=safe("B4",lambda:YouTubeAcquisitionEngine().run_once(20))
results["B5_judge_binder"]=safe("B5",lambda:JudgeRealBiomechanicsBinder().run_once(1000))
results["B6_real_valuation"]=safe("B6",lambda:RealValuationBinder().run_once())
results["C_pedigree_validation"]=safe("C",lambda:PedigreeSourceValidator().run_once())
results["D_market_prices"]=safe("D",lambda:MarketValuationRealPrices().run_once())
results["B6_real_valuation_after_market"]=safe("B6_2",lambda:RealValuationBinder().run_once())
results["GENETIC_GRAPH"]=safe("GRAPH",lambda:GeneticGraphBuilder().run_once())

after={t:count(t) for t in tables}
snap=ExecutiveSnapshot().build()

audit={
    "mission":"P5_6_MASTER_CONSOLIDATED_EXECUTION",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "before":before,
    "after":after,
    "growth":{t:after[t]-before[t] for t in tables},
    "results":results,
    "snapshot":snap
}

open("p56_master_consolidated_execution_audit.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2,default=str))

print(json.dumps({
    "mission":audit["mission"],
    "before":before,
    "after":after,
    "growth":audit["growth"],
    "critical_gaps":snap.get("critical_gaps"),
    "audit_file":"p56_master_consolidated_execution_audit.json"
},indent=2,ensure_ascii=False,default=str))
