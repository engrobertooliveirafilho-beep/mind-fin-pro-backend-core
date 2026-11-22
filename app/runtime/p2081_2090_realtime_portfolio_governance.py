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
        os.environ[key] = value
    return dict(ABSOLUTE_LOCKS)


def assert_no_financial_execution() -> None:
    # Fail closed on explicit unsafe environment before initializing missing locks.
    for key, expected in ABSOLUTE_LOCKS.items():
        observed = os.environ.get(key)
        if observed is not None and observed != expected:
            raise RuntimeError(f"{key}_LOCK_BREACH")
    enforce_paper_only()


def load_json(path: str) -> Any:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return json.loads(p.read_text(encoding="utf-8"))


def extract_specialists(raw: Any) -> List[Dict[str, Any]]:
    candidates = raw if isinstance(raw, list) else None
    if isinstance(raw, dict):
        for key in ["specialists", "final_specialists", "portfolio", "locked_specialists"]:
            if isinstance(raw.get(key), list):
                candidates = raw[key]
                break
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("REALDNA_SPECIALISTS_MISSING_OR_EMPTY")
    seen = set()
    for index, specialist in enumerate(candidates):
        if not isinstance(specialist, dict):
            raise ValueError(f"REALDNA_SPECIALIST_INVALID:{index}")
        sid = str(specialist.get("id") or specialist.get("specialist_id") or "").strip()
        if not sid:
            raise ValueError(f"REALDNA_SPECIALIST_ID_MISSING:{index}")
        if sid in seen:
            raise ValueError(f"REALDNA_SPECIALIST_ID_DUPLICATE:{sid}")
        seen.add(sid)
    return candidates


def extract_runtime_metrics(raw: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, dict) or not isinstance(raw.get("metrics"), dict):
        raise ValueError("P2071_RUNTIME_METRICS_MISSING")
    metrics = raw["metrics"]
    required = ["cycles", "frames_built", "signals_generated", "closed_trades",
                "open_positions", "initial_equity", "final_mark_to_market_equity",
                "paper_mark_to_market_pnl", "drawdown_pct", "drawdown_abs",
                "peak_equity", "trough_equity"]
    missing = [key for key in required if key not in metrics]
    if missing:
        raise ValueError("P2071_RUNTIME_METRICS_INCOMPLETE:" + ",".join(missing))

    # Prevent NaN/Infinity and coerced fractional counters from entering
    # risk governance decisions or falsely satisfying thresholds.
    for key in required:
        value = metrics[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("P2071_RUNTIME_METRIC_INVALID:" + key)
    for key in ("cycles", "frames_built", "signals_generated", "closed_trades", "open_positions"):
        value = metrics[key]
        if value < 0 or int(value) != value:
            raise ValueError("P2071_RUNTIME_COUNTER_INVALID:" + key)
    for key in ("initial_equity", "final_mark_to_market_equity", "peak_equity", "trough_equity"):
        if metrics[key] <= 0:
            raise ValueError("P2071_RUNTIME_EQUITY_INVALID:" + key)
    # Historical peak-to-trough drawdown is required: a later recovery
    # must not conceal an earlier risk-limit breach.
    historical_dd = metrics.get("max_drawdown_pct")
    if isinstance(historical_dd, bool) or not isinstance(historical_dd, (int, float)) or not math.isfinite(historical_dd):
        raise ValueError("P2071_MAX_DRAWDOWN_MISSING_OR_INVALID")
    if historical_dd < 0 or historical_dd > 1:
        raise ValueError("P2071_MAX_DRAWDOWN_OUT_OF_RANGE")
    if historical_dd + 1e-8 < abs(metrics["drawdown_pct"]):
        raise ValueError("P2071_MAX_DRAWDOWN_INCONSISTENT")
    # P2071 emits signed current drawdown (<= 0), unlike max drawdown
    # magnitude (>= 0). Preserve its historical contract.
    if metrics["drawdown_pct"] > 0 or metrics["drawdown_abs"] > 0:
        raise ValueError("P2071_RUNTIME_DRAWDOWN_INVALID")

    return {
        "cycles": int(metrics.get("cycles", 0)),
        "frames_built": int(metrics.get("frames_built", 0)),
        "signals_generated": int(metrics.get("signals_generated", 0)),
        "closed_trades": int(metrics.get("closed_trades", 0)),
        "open_positions": int(metrics.get("open_positions", 0)),
        "initial_equity": float(metrics.get("initial_equity", 100000.0)),
        "final_mark_to_market_equity": float(
            metrics.get("final_mark_to_market_equity", metrics.get("final_realized_equity", 100000.0))
        ),
        "paper_mark_to_market_pnl": float(metrics.get("paper_mark_to_market_pnl", 0.0)),
        "drawdown_pct": float(metrics.get("drawdown_pct", 0.0)),
        "drawdown_abs": float(metrics.get("drawdown_abs", 0.0)),
        "max_drawdown_pct": float(metrics["max_drawdown_pct"]),
        "peak_equity": float(metrics.get("peak_equity", 100000.0)),
        "trough_equity": float(metrics.get("trough_equity", 100000.0)),
    }


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
        ok = current_dd >= max_drawdown_pct and runtime["max_drawdown_pct"] <= abs(max_drawdown_pct)

        return GovernanceDecision(
            component="P2084_RISK_ENGINE",
            status="PASS" if ok else "FAIL",
            reason="RISK_WITHIN_LIMITS" if ok else "DRAWDOWN_LIMIT_BREACH",
            payload={
                "drawdown_pct": current_dd,
                "max_drawdown_pct": max_drawdown_pct,
                "observed_max_drawdown_pct": runtime["max_drawdown_pct"],
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

        if runtime["drawdown_pct"] < -0.05 or runtime["max_drawdown_pct"] > 0.05:
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

        # Exercise real governance engines instead of trusting hard-coded PASS flags.
        exposure_breach = dict(runtime, open_positions=4)
        drawdown_breach = dict(runtime, drawdown_pct=-0.06,
                               max_drawdown_pct=max(runtime["max_drawdown_pct"], 0.06))
        historical_breach = dict(runtime, drawdown_pct=0.0,
                                max_drawdown_pct=0.08)
        simulations = {
            "exposure_limit_breach_detected":
                ExposureMonitor().evaluate(exposure_breach).status == "FAIL",
            "drawdown_limit_breach_detected":
                RiskEngine().evaluate(drawdown_breach).status == "FAIL",
            "historical_drawdown_breach_detected":
                RiskEngine().evaluate(historical_breach).status == "FAIL",
            "historical_anomaly_detected":
                "DRAWDOWN_OVER_LIMIT" in AnomalyDetection().evaluate(historical_breach).payload["anomalies"],
        }
        ok = all(simulations.values())

        return GovernanceDecision(
            component="P2089_FAILURE_SIMULATION",
            status="PASS" if ok else "FAIL",
            reason="BEHAVIORAL_FAILURE_SIMULATION_OK" if ok else "FAILURE_SIMULATION_FAIL",
            payload=simulations,
        )


def certify_governance(decisions: List[GovernanceDecision]) -> GovernanceDecision:
    assert_no_financial_execution()

    failed = [x.component for x in decisions if x.status != "PASS"]
    present = [x.component for x in decisions]
    required = {f"P{i}_" for i in range(2081, 2090)}
    complete = len(present) == 9 and len(set(present)) == 9 and all(
        any(component.startswith(prefix) for component in present) for prefix in required
    )
    ok = complete and not failed

    return GovernanceDecision(
        component="P2090_GOVERNANCE_CERTIFICATION",
        status="PASS" if ok else "FAIL",
        reason="REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED" if ok else "GOVERNANCE_NOT_CERTIFIED",
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
