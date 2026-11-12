"""ET665 M8: explicit offline historical PAPER replay, never a live order router.

Historical candidate fills are not forecasts. Caller must explicitly authorize
replay; the existing ExecutionGateway remains the sole risk/broker authority.
"""
import json
import math
import hashlib
from pathlib import Path

from mind_trader.app.execution.gateway import ExecutionGateway


def _positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def replay_candidate_to_paper(candidate, gateway, *, risk_amount, stop_distance,
                              reward_multiple=2.5, regime_report=None,
                              genome=None, authorize_offline_replay=False,
                              telemetry_path=None, quantity=None, quote_to_account_rate=None,
                              contract_multiplier=None):
    """Replay ONE historical candidate, fail closed on any missing evidence.

    No settlement is fabricated: closing a PAPER position requires a separately
    evidenced exit and an explicit settle_paper_order call.
    """
    result = {"decision": "BLOCKED_M8_PRECHECK", "production": "BLOCKED",
              "real_broker_routing": "DISABLED", "reservation_id": None}
    def emit():
        if telemetry_path is not None:
            p = Path(telemetry_path)
            if p.exists():
                raise FileExistsError("M8_TELEMETRY_IMMUTABLE")
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("x", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, sort_keys=True)
        return result

    if not authorize_offline_replay or not isinstance(gateway, ExecutionGateway):
        result["reason"] = "OFFLINE_REPLAY_NOT_AUTHORIZED"
        return emit()
    if not isinstance(candidate, dict) or candidate.get("decision") != "RESEARCH_ONLY_NOT_ROUTED" or candidate.get("real_orders") != "FORBIDDEN":
        result["reason"] = "INVALID_RESEARCH_CANDIDATE"
        return emit()
    if candidate.get("side") not in ("BUY", "SELL") or not isinstance(candidate.get("candidate_id"), str) or len(candidate["candidate_id"]) != 64:
        result["reason"] = "INVALID_CANDIDATE_ID_OR_SIDE"
        return emit()
    if not isinstance(candidate.get("signal_ts"), str) or not isinstance(candidate.get("fill_ts"), str) or candidate["signal_ts"] >= candidate["fill_ts"]:
        result["reason"] = "NON_CHRONOLOGICAL_CANDIDATE"
        return emit()
    if not all(_positive(v) for v in (candidate.get("simulated_fill"), risk_amount, stop_distance, reward_multiple)):
        result["reason"] = "INVALID_PRICE_OR_RISK"
        return emit()
    if reward_multiple < 2:
        result["reason"] = "INSUFFICIENT_REWARD_MULTIPLE"
        return emit()
    if not isinstance(candidate.get("symbol"), str) or not candidate["symbol"] or candidate.get("strategy_id") != "SMA_CROSS":
        result["reason"] = "INVALID_INSTRUMENT_OR_STRATEGY"
        return emit()
    if not isinstance(regime_report, dict) or not isinstance(genome, dict) or regime_report.get("trade_allowed") is not True or regime_report.get("regime") != genome.get("regime"):
        result["reason"] = "REGIME_NOT_VERIFIED"
        return emit()
    if genome.get("edge_claim") != "NONE" or not genome.get("genome_id"):
        result["reason"] = "INVALID_GENOME"
        return emit()
    if not isinstance(candidate.get("costs"), dict) or not all(
        type(candidate["costs"].get(k)) in (int, float) and math.isfinite(candidate["costs"][k]) and candidate["costs"][k] >= 0
        for k in ("spread", "slippage", "commission")
    ):
        result["reason"] = "INVALID_COST_EVIDENCE"
        return emit()
    cfg = gateway.ftmo_ruleset
    if not isinstance(cfg, dict) or not gateway.ftmo_config_valid.get("valid") or any(
        abs(float(cfg[k]) - float(candidate["costs"][k])) > 1e-12
        for k in ("spread", "slippage", "commission")
    ):
        result["reason"] = "COST_CONFIG_DRIFT"
        return emit()
    canonical = {k:v for k,v in candidate.items() if k != "candidate_id"}
    digest = hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if digest != candidate["candidate_id"]:
        result["reason"] = "CANDIDATE_INTEGRITY_MISMATCH"
        return emit()
    side = candidate["side"]
    friction = float(candidate["costs"]["spread"]) / 2 + float(candidate["costs"]["slippage"])
    # M7 price already includes entry friction; gateway applies it exactly once.
    price = float(candidate["simulated_fill"]) - friction if side == "BUY" else float(candidate["simulated_fill"]) + friction
    if not _positive(price):
        result["reason"] = "INVALID_RAW_ENTRY"
        return emit()
    stop = price - stop_distance if side == "BUY" else price + stop_distance
    target = price + stop_distance * reward_multiple if side == "BUY" else price - stop_distance * reward_multiple
    if not _positive(stop) or not _positive(target):
        result["reason"] = "INVALID_STOP_OR_TARGET"
        return emit()
    state = gateway.paper._read_session()
    if not state or state.get("status") != "OPEN":
        result["reason"] = "NO_VALID_PAPER_SESSION"
        return emit()
    trade = {
        "symbol": candidate["symbol"], "strategy_id": candidate["strategy_id"],
        "client_order_id": "M8-" + candidate["candidate_id"][:64],
        "side": side, "entry": price, "stop": stop, "target": target,
        "risk_amount": float(risk_amount),
        "daily_trades": state["trades"], "daily_pnl": state["daily_pnl"],
        "total_pnl": state["daily_pnl"], "loss_streak": state["loss_streak"],
        "open_risk": sum(x["risk"] for x in state.get("pending_paper_orders", [])),
        "session_allowed": True, "news_blocked": False,
    }
    if quantity is not None:
        trade["quantity"] = quantity
    if quote_to_account_rate is not None:
        trade["quote_to_account_rate"] = quote_to_account_rate
    if contract_multiplier is not None:
        trade["contract_multiplier"] = contract_multiplier
    response = gateway.submit_order("PAPER", trade, regime_report, genome)
    result["decision"] = response.get("decision", "BLOCKED_GATEWAY_NO_DECISION")
    result["gateway_execution_id"] = response.get("execution_id")
    result["reservation_id"] = response.get("paper_reservation_id")
    result["checks"] = response.get("checks", [])
    result["candidate_id"] = candidate["candidate_id"]
    result["mode"] = "PAPER"
    return emit()


def replay_financially_verified_candidate(candidate, gateway, *,
                                         quantity, quote_to_account_rate,
                                         contract_multiplier, risk_amount,
                                         stop_distance, reward_multiple=2.5,
                                         regime_report=None, genome=None,
                                         authorize_offline_replay=False):
    """Strict PAPER entrypoint. Requires explicit financial unit contract."""
    from mind_trader.app.risk.paper_financial_contract import verify_paper_financial_contract
    blocked={"decision":"BLOCK_FINANCIAL_REPLAY","production":"BLOCKED",
             "real_broker_routing":"DISABLED","reservation_id":None}
    if not authorize_offline_replay or not isinstance(gateway,ExecutionGateway):
        return dict(blocked,reason="NOT_AUTHORIZED")
    if not isinstance(candidate,dict) or candidate.get("side") not in ("BUY","SELL"):
        return dict(blocked,reason="INVALID_CANDIDATE")
    costs=candidate.get("costs")
    if not isinstance(costs,dict) or not all(type(costs.get(k)) in (int,float) and math.isfinite(costs[k]) and costs[k]>=0 for k in ("spread","slippage","commission")):
        return dict(blocked,reason="INVALID_COSTS")
    if not all(_positive(v) for v in (candidate.get("simulated_fill"),risk_amount,stop_distance,reward_multiple)):
        return dict(blocked,reason="INVALID_INPUT")
    side=candidate["side"]
    friction=costs["spread"]/2+costs["slippage"]
    raw_entry=candidate["simulated_fill"]-friction if side=="BUY" else candidate["simulated_fill"]+friction
    stop=raw_entry-stop_distance if side=="BUY" else raw_entry+stop_distance
    contract=verify_paper_financial_contract(side=side,entry_fill=candidate["simulated_fill"],
        stop=stop,quantity=quantity,quote_to_account_rate=quote_to_account_rate,
        contract_multiplier=contract_multiplier,commission_per_unit_per_side=costs["commission"],
        spread=costs["spread"],slippage=costs["slippage"],reserved_risk_account=risk_amount)
    if contract["decision"]!="FINANCIAL_CONTRACT_VALIDATED":
        return dict(blocked,reason=contract.get("reason"),financial_contract=contract)
    # Do not bypass the existing M8 integrity, regime, FTMO and broker gates.
    result=replay_candidate_to_paper(candidate,gateway,risk_amount=risk_amount,
        stop_distance=stop_distance,reward_multiple=reward_multiple,
        regime_report=regime_report,genome=genome,
        authorize_offline_replay=True,quantity=quantity,
        quote_to_account_rate=quote_to_account_rate,
        contract_multiplier=contract_multiplier)
    result["financial_contract"]=contract
    return result
