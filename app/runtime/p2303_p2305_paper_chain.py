"""P2303-P2305 integration: offline evidence chain; never broker-connected."""
from app.runtime.p2303_mt5_consumption_audit import audit_consumption
from app.runtime.p2304_paper_performance_gate import audit_paper_performance
from app.runtime.p2305_ftmo_twin_gate import reconcile_twin

def reconcile_paper_chain(mt5_record, mt5_logs, performance_summary, performance_ledger, risk_ledger, twin_summary, twin_state, twin_rules):
    mt5 = audit_consumption(mt5_record, mt5_logs)
    performance = audit_paper_performance(performance_summary, performance_ledger, risk_ledger)
    twin = reconcile_twin(twin_summary, twin_state, twin_rules)
    if performance["signals_consumed_reported"] != twin["consumed_trades"]:
        raise ValueError("P2305_CROSS_STAGE_COUNT_MISMATCH")
    if performance["signals_consumed_reported"] != 0 or mt5["terminal_read_proven"]:
        raise ValueError("P2305_UNVERIFIED_CONSUMPTION")
    return {"status":"PAPER_EVIDENCE_CHAIN_RECONCILED_NOT_CERTIFIED",
            "p2303":mt5["status"],"p2304":performance["status"],
            "p2305":twin["status"],"orders_authorized":0,
            "ftmo_challenge_certified":False,"e2e_certified":False}
