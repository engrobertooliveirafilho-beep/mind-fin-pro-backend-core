import json, datetime, traceback
from app.mind.p5_5u_real_result_claim_extractor.extractor import RealResultClaimExtractor
from app.mind.p5_5v_pedigree_extractor.extractor import PedigreeExtractor
from app.mind.p5_6c_pedigree_source_validation.validator import PedigreeSourceValidator
from app.mind.p5_5x_genetic_graph_builder.graph import GeneticGraphBuilder
from app.mind.p5_6b6_real_valuation_binder.binder import RealValuationBinder
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

def safe(name, fn):
    try:
        return {"ok": True, "result": fn()}
    except Exception as e:
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()[-2000:]}

before = ExecutiveSnapshot().build()

results = {
    "claim_extractor": safe("claims", lambda: RealResultClaimExtractor().run_once(5000)),
    "pedigree_extractor": safe("pedigree", lambda: PedigreeExtractor().run_once()),
    "pedigree_validation": safe("validation", lambda: PedigreeSourceValidator().run_once()),
    "genetic_graph": safe("graph", lambda: GeneticGraphBuilder().run_once()),
    "valuation_rebuild": safe("valuation", lambda: RealValuationBinder().run_once())
}

after = ExecutiveSnapshot().build()

audit = {
    "mission": "P5.6E2_MASTER_GENETIC_EXPANSION",
    "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
    "before_counts": before["counts"],
    "after_counts": after["counts"],
    "growth": {k: after["counts"].get(k,0)-before["counts"].get(k,0) for k in after["counts"]},
    "results": results,
    "critical_gaps": after.get("critical_gaps")
}

open("p56e2_master_genetic_expansion_audit.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2,default=str))
print(json.dumps({k:audit[k] for k in ["mission","before_counts","after_counts","growth","critical_gaps"]},indent=2,ensure_ascii=False))
