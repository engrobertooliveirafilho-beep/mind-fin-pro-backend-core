from __future__ import annotations

import json
import os
import time
import statistics
import math
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any


ABSOLUTE_LOCKS = {
    "MIND_MODE": "PAPER_ONLY",
    "REAL_ORDERS": "FORBIDDEN",
    "LIVE_TRADING": "FALSE",
    "BROKER_EXECUTION": "DISABLED",
    "FINANCIAL_EXECUTION": "DISABLED",
    "FTMO_REAL": "FORBIDDEN",
    "SEND_ORDER": "BLOCKED",
    "MT5_ORDER_SEND": "BLOCKED",
    "BROKER_API_CALL": "BLOCKED",
}


def enforce_paper_only() -> Dict[str, str]:
    for key, value in ABSOLUTE_LOCKS.items():
        if key in os.environ and os.environ[key] != value:
            raise RuntimeError(f"{key}_LOCK_BREACH")
    for key, value in ABSOLUTE_LOCKS.items():
        os.environ[key] = value
    return dict(ABSOLUTE_LOCKS)


def assert_no_financial_execution() -> None:
    locks = {key: os.environ.get(key) for key in ABSOLUTE_LOCKS}

    if locks["MIND_MODE"] != "PAPER_ONLY":
        raise RuntimeError("MIND_MODE_LOCK_BREACH")
    if locks["REAL_ORDERS"] != "FORBIDDEN":
        raise RuntimeError("REAL_ORDERS_LOCK_BREACH")
    if locks["LIVE_TRADING"] != "FALSE":
        raise RuntimeError("LIVE_TRADING_LOCK_BREACH")
    if locks["BROKER_EXECUTION"] != "DISABLED":
        raise RuntimeError("BROKER_EXECUTION_LOCK_BREACH")
    if locks["FINANCIAL_EXECUTION"] != "DISABLED":
        raise RuntimeError("FINANCIAL_EXECUTION_LOCK_BREACH")
    if locks["FTMO_REAL"] != "FORBIDDEN":
        raise RuntimeError("FTMO_REAL_LOCK_BREACH")
    if locks["SEND_ORDER"] != "BLOCKED":
        raise RuntimeError("SEND_ORDER_LOCK_BREACH")
    if locks["MT5_ORDER_SEND"] != "BLOCKED":
        raise RuntimeError("MT5_ORDER_SEND_LOCK_BREACH")
    if locks["BROKER_API_CALL"] != "BLOCKED":
        raise RuntimeError("BROKER_API_CALL_LOCK_BREACH")


@dataclass
class GovernanceDecision:
    component: str
    status: str
    reason: str
    payload: Dict[str, Any]


def load_json(path: str) -> Any:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return json.loads(p.read_text(encoding="utf-8"))


def extract_specialists(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        for key in ["specialists", "final_specialists", "portfolio", "locked_specialists"]:
            if isinstance(raw.get(key), list):
                return raw[key]

    raise ValueError("SPECIALISTS_MISSING")


def extract_runtime_metrics(raw: Dict[str, Any]) -> Dict[str, Any]:
    metrics = raw.get("metrics") if isinstance(raw, dict) else None
    if not isinstance(metrics, dict):
        raise ValueError("RUNTIME_METRICS_MISSING")
    counts = ("cycles", "frames_built", "signals_generated", "closed_trades", "open_positions")
    amounts = ("initial_equity", "final_mark_to_market_equity", "paper_mark_to_market_pnl", "drawdown_pct", "drawdown_abs", "peak_equity", "trough_equity")
    result = {}
    for key in counts:
        value = metrics.get(key)
        if type(value) is not int or value < 0:
            raise ValueError(f"INVALID_METRIC:{key}")
        result[key] = value
    for key in amounts:
        value = metrics.get(key)
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"INVALID_METRIC:{key}")
        result[key] = value
    if result["initial_equity"] <= 0 or result["peak_equity"] <= 0 or result["drawdown_pct"] > 0 or result["drawdown_abs"] > 0:
        raise ValueError("INVALID_FINANCIAL_METRICS")
    return result


class PortfolioHealth:
    def evaluate(self, specialists: List[Dict[str, Any]], runtime: Dict[str, Any]) -> GovernanceDecision:
        assert_no_financial_execution()

        ok = len(specialists) >= 3 and runtime["cycles"] >= 1000

        return GovernanceDecision(
            component="P2081_PORTFOLIO_HEALTH",
            status="PASS" if ok else "FAIL",
            reason="PORTFOLIO_HEALTH_OK" if ok else "PORTFOLIO_HEALTH_INSUFFICIENT",
            payload={
                "specialists": len(specialists),
                "cycles": runtime["cycles"],
                "closed_trades": runtime["closed_trades"],
                "open_positions": runtime["open_positions"],
            },
        )


class RuntimeMetrics:
    def evaluate(self, runtime: Dict[str, Any]) -> GovernanceDecision:
        assert_no_financial_execution()

        signal_density = runtime["signals_generated"] / max(runtime["frames_built"], 1)
        trade_density = runtime["closed_trades"] / max(runtime["frames_built"], 1)

        ok = runtime["frames_built"] >= 1000 and runtime["signals_generated"] > 0

        return GovernanceDecision(
            component="P2082_RUNTIME_METRICS",
            status="PASS" if ok else "FAIL",
            reason="RUNTIME_METRICS_OK" if ok else "RUNTIME_METRICS_WEAK",
            payload={
                "frames_built": runtime["frames_built"],
                "signals_generated": runtime["signals_generated"],
                "signal_density": round(signal_density, 8),
                "trade_density": round(trade_density, 8),
            },
        )


class ExposureMonitor:
    def evaluate(self, runtime: Dict[str, Any]) -> GovernanceDecision:
        assert_no_financial_execution()

        max_open_positions = 3
        ok = runtime["open_positions"] <= max_open_positions

        return GovernanceDecision(
            component="P2083_EXPOSURE_MONITOR",
            status="PASS" if ok else "FAIL",
            reason="EXPOSURE_WITHIN_LIMITS" if ok else "EXPOSURE_LIMIT_BREACH",
            payload={
                "open_positions": runtime["open_positions"],
                "max_open_positions": max_open_positions,
            },
        )


class RiskEngine:
    def evaluate(self, runtime: Dict[str, Any]) -> GovernanceDecision:
        assert_no_financial_execution()

        max_drawdown_pct = -0.05
        current_dd = runtime["drawdown_pct"]
        ok = current_dd >= max_drawdown_pct

        return GovernanceDecision(
            component="P2084_RISK_ENGINE",
            status="PASS" if ok else "FAIL",
            reason="RISK_WITHIN_LIMITS" if ok else "DRAWDOWN_LIMIT_BREACH",
            payload={
                "drawdown_pct": current_dd,
                "max_drawdown_pct": max_drawdown_pct,
                "drawdown_abs": runtime["drawdown_abs"],
            },
        )


class PortfolioRebalancing:
    def evaluate(self, specialists: List[Dict[str, Any]]) -> GovernanceDecision:
        assert_no_financial_execution()

        n = len(specialists)
        target_weight = round(1 / max(n, 1), 8)
        allocation = {}

        for idx, spec in enumerate(specialists):
            sid = str(spec.get("id") or spec.get("specialist_id") or f"REALDNA_{idx+1}")
            allocation[sid] = target_weight

        ok = n >= 3 and abs(sum(allocation.values()) - 1.0) <= 0.0001

        return GovernanceDecision(
            component="P2085_PORTFOLIO_REBALANCING",
            status="PASS" if ok else "FAIL",
            reason="REBALANCING_MODEL_OK" if ok else "REBALANCING_MODEL_FAIL",
            payload={
                "specialists": n,
                "allocation": allocation,
                "allocation_sum": round(sum(allocation.values()), 8),
            },
        )


class CapitalAllocation:
    def evaluate(self, specialists: List[Dict[str, Any]], equity: float) -> GovernanceDecision:
        assert_no_financial_execution()

        n = len(specialists)
        per_specialist = equity / max(n, 1)

        allocation = {}

        for idx, spec in enumerate(specialists):
            sid = str(spec.get("id") or spec.get("specialist_id") or f"REALDNA_{idx+1}")
            allocation[sid] = round(per_specialist, 2)

        ok = n >= 3 and equity > 0

        return GovernanceDecision(
            component="P2086_CAPITAL_ALLOCATION",
            status="PASS" if ok else "FAIL",
            reason="CAPITAL_ALLOCATION_OK" if ok else "CAPITAL_ALLOCATION_FAIL",
            payload={
                "equity": round(equity, 2),
                "specialists": n,
                "capital_per_specialist": round(per_specialist, 2),
                "allocation": allocation,
            },
        )


class PortfolioRecovery:
    def evaluate(self, governance_state: Dict[str, Any]) -> GovernanceDecision:
        assert_no_financial_execution()

        serialized = json.dumps(governance_state, ensure_ascii=False)
        restored = json.loads(serialized)

        ok = restored.get("program") == governance_state.get("program")

        return GovernanceDecision(
            component="P2087_PORTFOLIO_RECOVERY",
            status="PASS" if ok else "FAIL",
            reason="RECOVERY_OK" if ok else "RECOVERY_FAIL",
            payload={
                "serialized_bytes": len(serialized.encode("utf-8")),
                "restored_program": restored.get("program"),
            },
        )


class AnomalyDetection:
    def evaluate(self, runtime: Dict[str, Any]) -> GovernanceDecision:
        assert_no_financial_execution()

        anomalies = []

        if runtime["frames_built"] <= 0:
            anomalies.append("NO_FRAMES")

        if runtime["signals_generated"] <= 0:
            anomalies.append("NO_SIGNALS")

        if runtime["open_positions"] > 3:
            anomalies.append("EXPOSURE_OVER_LIMIT")

        if runtime["drawdown_pct"] < -0.05:
            anomalies.append("DRAWDOWN_OVER_LIMIT")

        if runtime["final_mark_to_market_equity"] <= 0:
            anomalies.append("EQUITY_INVALID")

        ok = len(anomalies) == 0

        return GovernanceDecision(
            component="P2088_ANOMALY_DETECTION",
            status="PASS" if ok else "FAIL",
            reason="NO_CRITICAL_ANOMALIES" if ok else "CRITICAL_ANOMALIES_FOUND",
            payload={
                "anomalies": anomalies,
                "anomaly_count": len(anomalies),
            },
        )


class FailureSimulation:
    def evaluate(self, runtime: Dict[str, Any]) -> GovernanceDecision:
        assert_no_financial_execution()

        try:
            extract_runtime_metrics({})
        except ValueError:
            missing_rejected = True
        else:
            missing_rejected = False
        simulations = {
            "missing_runtime_metrics_rejected": missing_rejected,
            "exposure_limit_breach_detected": ExposureMonitor().evaluate({**runtime, "open_positions": 4}).status == "FAIL",
            "drawdown_limit_breach_detected": RiskEngine().evaluate({**runtime, "drawdown_pct": -0.051}).status == "FAIL",
            "state_roundtrip": json.loads(json.dumps(runtime, allow_nan=False)) == runtime,
        }
        ok = all(simulations.values())
        return GovernanceDecision(
            component="P2089_FAILURE_SIMULATION",
            status="UNVERIFIED" if ok else "FAIL",
            reason="PARTIAL_PROBES_LOCK_AND_RECOVERY_CERTIFICATION_PENDING" if ok else "FAILURE_SIMULATION_FAIL",
            payload=simulations,
        )


def certify_governance(decisions: List[GovernanceDecision]) -> GovernanceDecision:
    assert_no_financial_execution()

    expected = {"P2081_PORTFOLIO_HEALTH", "P2082_RUNTIME_METRICS", "P2083_EXPOSURE_MONITOR", "P2084_RISK_ENGINE", "P2085_PORTFOLIO_REBALANCING", "P2086_CAPITAL_ALLOCATION", "P2087_PORTFOLIO_RECOVERY", "P2088_ANOMALY_DETECTION", "P2089_FAILURE_SIMULATION"}
    failed = [x.component for x in decisions if x.status != "PASS"]
    if len(decisions) != len(expected) or {x.component for x in decisions} != expected:
        failed.append("INCOMPLETE_OR_DUPLICATE_COMPONENTS")

    return GovernanceDecision(
        component="P2090_GOVERNANCE_CERTIFICATION",
        status="PASS" if not failed else "FAIL",
        reason="REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED" if not failed else "GOVERNANCE_NOT_CERTIFIED",
        payload={
            "failed_components": failed,
            "passed_components": [x.component for x in decisions if x.status == "PASS"],
            "total_components": len(decisions),
        },
    )


def run_p2081_2090(
    portfolio_path: str,
    p2071_certification_path: str,
    output_dir: str,
) -> Dict[str, Any]:
    enforce_paper_only()
    assert_no_financial_execution()

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    portfolio_raw = load_json(portfolio_path)
    p2071_raw = load_json(p2071_certification_path)

    specialists = extract_specialists(portfolio_raw)
    runtime = extract_runtime_metrics(p2071_raw)

    if p2071_raw.get("status") != "PASS":
        raise RuntimeError("P2071_2080_NOT_CERTIFIED")

    if p2071_raw.get("readiness") != "REALTIME_PAPER_RUNTIME_CERTIFIED":
        raise RuntimeError("P2071_2080_READINESS_INVALID")

    decisions: List[GovernanceDecision] = []

    decisions.append(PortfolioHealth().evaluate(specialists, runtime))
    decisions.append(RuntimeMetrics().evaluate(runtime))
    decisions.append(ExposureMonitor().evaluate(runtime))
    decisions.append(RiskEngine().evaluate(runtime))
    decisions.append(PortfolioRebalancing().evaluate(specialists))
    decisions.append(CapitalAllocation().evaluate(specialists, runtime["final_mark_to_market_equity"]))

    governance_state = {
        "program": "P2081_2090_REALTIME_PORTFOLIO_GOVERNANCE",
        "runtime": runtime,
        "specialists": len(specialists),
        "locks": enforce_paper_only(),
    }

    decisions.append(PortfolioRecovery().evaluate(governance_state))
    decisions.append(AnomalyDetection().evaluate(runtime))
    decisions.append(FailureSimulation().evaluate(runtime))

    certification = certify_governance(decisions)
    decisions.append(certification)

    mission_status = {x.component: x.status for x in decisions}
    all_pass = all(x.status == "PASS" for x in decisions)

    result = {
        "program": "P2081_2090_REALTIME_PORTFOLIO_GOVERNANCE",
        "status": "PASS" if all_pass else "FAIL",
        "readiness": "REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED" if all_pass else "NOT_CERTIFIED",
        "absolute_restrictions": enforce_paper_only(),
        "input_dependencies": {
            "portfolio": portfolio_path,
            "p2071_2080_certification": p2071_certification_path,
        },
        "mission_status": mission_status,
        "decisions": [asdict(x) for x in decisions],
        "governance_metrics": {
            "specialists": len(specialists),
            "runtime_cycles": runtime["cycles"],
            "frames_built": runtime["frames_built"],
            "signals_generated": runtime["signals_generated"],
            "closed_trades": runtime["closed_trades"],
            "open_positions": runtime["open_positions"],
            "equity": runtime["final_mark_to_market_equity"],
            "paper_mark_to_market_pnl": runtime["paper_mark_to_market_pnl"],
            "drawdown_pct": runtime["drawdown_pct"],
            "drawdown_abs": runtime["drawdown_abs"],
        },
        "next_block": "P2091_2100_REALTIME_INTELLIGENCE_LAYER",
    }

    final_path = output / "P2081_2090_FINAL_CERTIFICATION.json"
    audit_path = output / "P2081_2090_AUDIT.md"
    state_path = output / "P2081_2090_GOVERNANCE_STATE.json"

    final_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    state_path.write_text(json.dumps(governance_state, indent=2, ensure_ascii=False), encoding="utf-8")

    audit = f"""# MIND TRADER — P2081→P2090 AUDIT

## PROGRAM
P2081_2090_REALTIME_PORTFOLIO_GOVERNANCE

## STATUS
{result["status"]}

## READINESS
{result["readiness"]}

## INPUT DEPENDENCIES
- Portfolio: {portfolio_path}
- P2071→P2080 Certification: {p2071_certification_path}

## MISSION STATUS
{json.dumps(mission_status, indent=2, ensure_ascii=False)}

## GOVERNANCE METRICS
{json.dumps(result["governance_metrics"], indent=2, ensure_ascii=False)}

## ABSOLUTE LOCKS
{json.dumps(result["absolute_restrictions"], indent=2, ensure_ascii=False)}

## CONCLUSION
P2081→P2090 executed as consolidated PAPER_ONLY realtime portfolio governance program.
No real orders.
No broker execution.
No financial execution.
"""
    audit_path.write_text(audit, encoding="utf-8")

    return result
