"""P2337: snapshot must preserve provisional ranking and block promotion/rebalance."""
def certify_snapshot(capture, ranking, rebalance):
    if not all(isinstance(x,dict) for x in (capture,ranking,rebalance)):
        raise ValueError("P2337_INVALID_EVIDENCE")
    if any(x.get("mode")!="PAPER_ONLY" or x.get("real_orders")!="FORBIDDEN" or x.get("ftmo_real")!="FORBIDDEN" for x in (capture,ranking,rebalance)):
        raise ValueError("P2337_UNSAFE_MODE")
    if capture.get("capture_status")!="CERTIFIED" or capture.get("deduplication")!="APPLIED":
        raise ValueError("P2337_CAPTURE_NOT_CERTIFIED")
    if capture.get("captured_results")!="1" or capture.get("unique_symbols")!="1":
        raise ValueError("P2337_CAPTURE_COUNT_MISMATCH")
    if ranking.get("status")!="CERTIFIED_PROVISIONAL_RANKING_SAMPLE_LIMITED" or ranking.get("total_trades")!="1" or ranking.get("rankable_symbols")!="0":
        raise ValueError("P2337_RANKING_EVIDENCE_MISMATCH")
    if rebalance.get("status")!="CERTIFIED_GATE_BLOCKED_BY_SAMPLE_SIZE" or rebalance.get("gate_decision")!="NO_REBALANCE" or rebalance.get("symbols_evaluated")!="1":
        raise ValueError("P2337_REBALANCE_EVIDENCE_MISMATCH")
    return {"status":"SNAPSHOT_CERTIFIED_BLOCKED_BY_SAMPLE_SIZE",
            "captured_results":1,"rankable_symbols":0,"rebalance":"NO_REBALANCE",
            "performance_certified":False,"capital_allocation_allowed":False,
            "edge_promotion_allowed":False,"e2e_certified":False}
