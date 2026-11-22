"""P2304: reconcile paper monitoring against actual consumption, never infer profits."""
from decimal import Decimal, InvalidOperation

def audit_paper_performance(summary, performance, risk):
    if not isinstance(summary,dict) or not isinstance(performance,(list,tuple)) or not isinstance(risk,(list,tuple)):
        raise ValueError("P2304_INVALID_INPUT")
    if summary.get("mode")!="PAPER_ONLY" or summary.get("real_orders")!="FORBIDDEN" or summary.get("ftmo_real")!="FORBIDDEN":
        raise ValueError("P2304_UNSAFE_SUMMARY")
    try:
        sent=int(summary["trades_sent"])
        consumed=int(summary["trades_consumed"])
        pending=int(summary["open_or_pending"])
    except (KeyError,TypeError,ValueError):
        raise ValueError("P2304_INVALID_COUNTS") from None
    if min(sent,consumed,pending)<0 or consumed>sent or pending>sent:
        raise ValueError("P2304_INVALID_COUNTS")
    if len(performance)!=sent:
        raise ValueError("P2304_LEDGER_MISMATCH")
    seen=set()
    closed=0
    for row in performance:
        if not isinstance(row,dict) or row.get("mode")!="PAPER_ONLY" or row.get("real_orders")!="FORBIDDEN" or row.get("ftmo_real")!="FORBIDDEN":
            raise ValueError("P2304_UNSAFE_TRADE")
        signal_id=row.get("signal_id")
        if not isinstance(signal_id,str) or not signal_id or signal_id in seen:
            raise ValueError("P2304_DUPLICATE_TRADE")
        seen.add(signal_id)
        if row.get("trade_status")=="NOT_CONSUMED_YET":
            if row.get("consumption_status")!="PENDING_MT5_CONSUMPTION" or str(row.get("pnl")) not in ("0","0.0") or str(row.get("pnl_pct")) not in ("0","0.0"):
                raise ValueError("P2304_UNVERIFIED_PNL")
        elif row.get("trade_status")=="CLOSED":
            closed+=1
        else:
            raise ValueError("P2304_UNKNOWN_STATUS")
    if closed>consumed or consumed+pending!=sent:
        raise ValueError("P2304_INCONSISTENT_LEDGER")
    metrics={row.get("metric"):row.get("value") for row in risk if isinstance(row,dict)}
    if len(metrics)!=len(risk) or metrics.get("real_orders")!="FORBIDDEN" or metrics.get("ftmo_real")!="FORBIDDEN" or str(metrics.get("trades_consumed"))!=str(consumed):
        raise ValueError("P2304_RISK_LEDGER_MISMATCH")
    return {"status":"PAPER_PERFORMANCE_NOT_VERIFIED" if not closed else "CLOSED_TRADES_NEED_INDEPENDENT_FILL_PROOF",
            "signals_sent":sent,"signals_consumed_reported":consumed,"closed_trades_reported":closed,
            "profit_factor_certified":False,"ftmo_compliance_certified":False,
            "performance_certified":False,"orders_authorized":0,"e2e_certified":False}
