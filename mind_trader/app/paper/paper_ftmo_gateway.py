"""P8.49 PAPER-only FTMO gateway; no broker or network dispatch."""
import math
from mind_trader.app.risk.ftmo_ruleset import load_ftmo_config, audit_rule_application

def evaluate_paper_intent(session, intent, audit_path):
    if not isinstance(intent,dict):
        return {"allowed":False,"decision":"BLOCK_INVALID_INTENT","production":"BLOCKED"}
    if intent.get("mode") != "PAPER" or intent.get("account_id") != "PAPER_FTMO_SIM":
        return {"allowed":False,"decision":"BLOCK_NON_PAPER_INTENT","production":"BLOCKED"}
    if intent.get("side") not in ("BUY","SELL") or not isinstance(intent.get("symbol"),str) or not intent["symbol"].strip():
        return {"allowed":False,"decision":"BLOCK_INVALID_INTENT","production":"BLOCKED"}
    risk=intent.get("risk_amount")
    if type(risk) not in (int,float) or not math.isfinite(risk) or risk <= 0:
        return {"allowed":False,"decision":"BLOCK_INVALID_RISK","production":"BLOCKED"}
    cfg,status=load_ftmo_config(session.ftmo_config_path)
    if not cfg or not status.get("valid"):
        return {"allowed":False,"decision":"BLOCK_INVALID_FTMO_CONFIG","production":"BLOCKED"}
    state=session._read_session()
    if not isinstance(state,dict) or state.get("status") != "OPEN":
        return {"allowed":False,"decision":"BLOCK_NO_OPEN_SESSION","production":"BLOCKED"}
    gate=session.pre_trade_check(risk)
    if not gate.get("allowed"):
        return {"allowed":False,"decision":gate["decision"],"production":"BLOCKED"}
    # Derive cumulative account P&L from ledger; never trust a caller's number.
    total_pnl=session.account_total_pnl()
    if type(total_pnl) not in (int,float) or not math.isfinite(total_pnl):
        return {"allowed":False,"decision":"BLOCK_TOTAL_PNL_UNVERIFIED","production":"BLOCKED"}
    claimed_total=intent.get("account_total_pnl")
    if claimed_total is not None and (type(claimed_total) not in (int,float) or
                                      not math.isfinite(claimed_total) or claimed_total != total_pnl):
        return {"allowed":False,"decision":"BLOCK_TOTAL_PNL_MISMATCH","production":"BLOCKED"}
    audit=audit_rule_application({
        "symbol":intent["symbol"],"risk_amount":risk,
        "daily_pnl":state["daily_pnl"],"total_pnl":total_pnl,
        "daily_trades":state["trades"],"stop":intent.get("stop")
    },cfg,path=audit_path)
    if audit["decision"] != "ALLOW_FTMO_SIMULATION":
        return {"allowed":False,"decision":"BLOCK_FTMO_RULES","production":"BLOCKED","audit":audit}
    return {"allowed":True,"decision":"ALLOW_PAPER_INTENT","production":"BLOCKED","session_id":gate["session_id"],"audit":audit}
