"""P2391/P2397 lineage reconciliation: validates source metadata, not trades."""
import json
from pathlib import Path

def validate(manifest):
    o=manifest["observed"]; l=manifest["limits"]
    checks=[
      manifest["source_edge"]=="P2391_8149352397",
      o["source_edge_event_rows"]==152==o["source_edge_samples_aggregate"],
      o["source_edge_direction"]=="BUY_PAPER",
      o["source_edge_key"]=="US_AFTERNOON|LIQUIDITY_SWEEP_REVERSAL_DOWN|LIQUIDITY_REVERSAL_ENTRY|DISTRIBUTION->BALANCE",
      o["p2397_source_cluster"]=="P2393_CLUSTER_AB78986FAD66",
      o["p2397_decision"]=="OBSERVE_SCORE",
      o["p2397_hypotheses"]==3,
      l["event_rows_are_fills"] is False,
      l["entry_exit_prices_available"] is False,
      l["pnl_per_event_available"] is False,
      l["p2400_candidate_ancestry_proven"] is False,
      l["runtime_promotion_allowed"] is False]
    return {"metadata_reconciled":all(checks),"checks":len(checks),
      "strategy_replay_certified":False,"performance_certified":False,
      "portfolio_correlation_certified":False,"runtime_promotion_allowed":False}

if __name__=="__main__":
    p=Path(__file__).with_name("lineage_manifest.json")
    print(json.dumps(validate(json.loads(p.read_text())),indent=2))
