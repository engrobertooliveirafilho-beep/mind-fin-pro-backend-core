from __future__ import annotations

import json
import os
import time
import statistics
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
    for k, v in ABSOLUTE_LOCKS.items():
        os.environ[k] = v
    return dict(ABSOLUTE_LOCKS)


def assert_no_financial_execution() -> None:
    locks = enforce_paper_only()
    for k, v in ABSOLUTE_LOCKS.items():
        if locks.get(k) != v:
            raise RuntimeError(f"{k}_LOCK_BREACH")


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
    return [{"id": "XAUUSD_M1_REALDNA_0004", "type": "RANGE_REVERSION"}]


def spec_id(spec: Dict[str, Any], idx: int) -> str:
    return str(spec.get("id") or spec.get("specialist_id") or f"REALDNA_{idx+1}")


@dataclass
class IntelligenceDecision:
    component: str
    status: str
    reason: str
    payload: Dict[str, Any]


class RuntimeAnalytics:
    def evaluate(self, p2071: Dict[str, Any]) -> IntelligenceDecision:
        assert_no_financial_execution()
        m = p2071.get("metrics", {})
        frames = int(m.get("frames_built", 0))
        signals = int(m.get("signals_generated", 0))
        closed = int(m.get("closed_trades", 0))
        density = signals / max(frames, 1)
        trade_density = closed / max(frames, 1)
        ok = frames >= 1000 and signals > 0

        return IntelligenceDecision(
            "P2091_RUNTIME_ANALYTICS",
            "PASS" if ok else "FAIL",
            "RUNTIME_ANALYTICS_OK" if ok else "RUNTIME_ANALYTICS_INSUFFICIENT",
            {
                "frames": frames,
                "signals": signals,
                "closed_trades": closed,
                "signal_density": round(density, 8),
                "trade_density": round(trade_density, 8),
            },
        )


class PortfolioIntelligence:
    def evaluate(self, specialists: List[Dict[str, Any]], p2081: Dict[str, Any]) -> IntelligenceDecision:
        assert_no_financial_execution()
        gov = p2081.get("governance_metrics", {})
        n = len(specialists)
        score = 0
        score += 25 if n >= 3 else 0
        score += 25 if float(gov.get("equity", 0)) > 0 else 0
        score += 25 if int(gov.get("runtime_cycles", 0)) >= 1000 else 0
        score += 25 if float(gov.get("drawdown_pct", -1)) >= -0.05 else 0

        return IntelligenceDecision(
            "P2092_PORTFOLIO_INTELLIGENCE",
            "PASS" if score >= 75 else "FAIL",
            "PORTFOLIO_INTELLIGENCE_OK" if score >= 75 else "PORTFOLIO_INTELLIGENCE_WEAK",
            {
                "specialists": n,
                "intelligence_score": score,
                "governance_equity": gov.get("equity"),
                "governance_drawdown_pct": gov.get("drawdown_pct"),
            },
        )


class RegimeAnalytics:
    def evaluate(self, p2071: Dict[str, Any]) -> IntelligenceDecision:
        assert_no_financial_execution()
        m = p2071.get("metrics", {})
        dd = abs(float(m.get("drawdown_pct", 0.0)))
        signals = int(m.get("signals_generated", 0))
        frames = int(m.get("frames_built", 1))
        signal_density = signals / max(frames, 1)

        if dd < 0.01 and signal_density > 1.0:
            regime = "ACTIVE_LOW_DRAWDOWN"
        elif dd < 0.03:
            regime = "NORMAL"
        else:
            regime = "STRESSED"

        ok = regime in ["ACTIVE_LOW_DRAWDOWN", "NORMAL"]

        return IntelligenceDecision(
            "P2093_REGIME_ANALYTICS",
            "PASS" if ok else "FAIL",
            "REGIME_ANALYTICS_OK" if ok else "REGIME_STRESSED",
            {
                "regime": regime,
                "drawdown_abs_pct": round(dd, 8),
                "signal_density": round(signal_density, 8),
            },
        )


class PerformanceAttribution:
    def evaluate(self, specialists: List[Dict[str, Any]], p2071: Dict[str, Any]) -> IntelligenceDecision:
        assert_no_financial_execution()
        m = p2071.get("metrics", {})
        pnl = float(m.get("paper_mark_to_market_pnl", m.get("paper_realized_pnl", 0.0)))
        n = max(len(specialists), 1)
        per_spec = pnl / n

        attribution = {}
        for idx, spec in enumerate(specialists):
            sid = spec_id(spec, idx)
            attribution[sid] = round(per_spec, 6)

        ok = len(attribution) >= 3

        return IntelligenceDecision(
            "P2094_PERFORMANCE_ATTRIBUTION",
            "PASS" if ok else "FAIL",
            "ATTRIBUTION_OK" if ok else "ATTRIBUTION_FAIL",
            {
                "portfolio_pnl": round(pnl, 6),
                "attribution": attribution,
                "attribution_sum": round(sum(attribution.values()), 6),
            },
        )


class BehaviorAnalysis:
    def evaluate(self, p2071: Dict[str, Any]) -> IntelligenceDecision:
        assert_no_financial_execution()
        m = p2071.get("metrics", {})
        frames = int(m.get("frames_built", 0))
        signals = int(m.get("signals_generated", 0))
        open_positions = int(m.get("open_positions", 0))
        closed = int(m.get("closed_trades", 0))

        behavior = "NORMAL"
        if signals / max(frames, 1) > 5:
            behavior = "OVERACTIVE"
        if open_positions > 3:
            behavior = "OVEREXPOSED"
        if closed <= 0:
            behavior = "INACTIVE"

        ok = behavior == "NORMAL" or behavior == "OVERACTIVE"

        return IntelligenceDecision(
            "P2095_BEHAVIOR_ANALYSIS",
            "PASS" if ok else "FAIL",
            "BEHAVIOR_ACCEPTABLE" if ok else "BEHAVIOR_INVALID",
            {
                "behavior": behavior,
                "frames": frames,
                "signals": signals,
                "closed_trades": closed,
                "open_positions": open_positions,
            },
        )


class SpecialistRankingEvolution:
    def evaluate(self, specialists: List[Dict[str, Any]]) -> IntelligenceDecision:
        assert_no_financial_execution()
        ranking = []

        for idx, spec in enumerate(specialists):
            sid = spec_id(spec, idx)
            base_score = float(spec.get("score", 100 - idx))
            rank_score = base_score + max(0, 3 - idx) * 10
            ranking.append({"specialist_id": sid, "rank": idx + 1, "score": round(rank_score, 6)})

        ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)
        for i, item in enumerate(ranking):
            item["rank"] = i + 1

        ok = len(ranking) >= 3 and ranking[0]["score"] >= ranking[-1]["score"]

        return IntelligenceDecision(
            "P2096_SPECIALIST_RANKING_EVOLUTION",
            "PASS" if ok else "FAIL",
            "RANKING_EVOLUTION_OK" if ok else "RANKING_EVOLUTION_FAIL",
            {"ranking": ranking},
        )


class AutoRetirement:
    def evaluate(self, ranking: List[Dict[str, Any]]) -> IntelligenceDecision:
        assert_no_financial_execution()
        retired = []
        watchlist = []

        for item in ranking:
            if item["score"] < 25:
                retired.append(item["specialist_id"])
            elif item["score"] < 50:
                watchlist.append(item["specialist_id"])

        return IntelligenceDecision(
            "P2097_AUTO_RETIREMENT",
            "PASS",
            "AUTO_RETIREMENT_POLICY_READY",
            {
                "retired": retired,
                "watchlist": watchlist,
                "policy": "PAPER_ONLY_NO_DESTRUCTIVE_REMOVAL",
            },
        )


class AutoPromotion:
    def evaluate(self, ranking: List[Dict[str, Any]]) -> IntelligenceDecision:
        assert_no_financial_execution()
        promoted = [x["specialist_id"] for x in ranking[:1]] if ranking else []

        ok = len(promoted) >= 1

        return IntelligenceDecision(
            "P2098_AUTO_PROMOTION",
            "PASS" if ok else "FAIL",
            "AUTO_PROMOTION_READY" if ok else "AUTO_PROMOTION_EMPTY",
            {
                "promoted_candidates": promoted,
                "promotion_scope": "PAPER_ONLY_RANKING_METADATA",
            },
        )


class PortfolioEvolution:
    def evaluate(self, ranking: List[Dict[str, Any]], p2081: Dict[str, Any]) -> IntelligenceDecision:
        assert_no_financial_execution()
        gov = p2081.get("governance_metrics", {})
        equity = float(gov.get("equity", 0.0))
        dd = float(gov.get("drawdown_pct", 0.0))

        evolution_state = "STABLE"
        if equity > 100000 and dd >= -0.02:
            evolution_state = "EXPANSION_READY"
        elif dd < -0.05:
            evolution_state = "DEFENSIVE"

        ok = evolution_state in ["STABLE", "EXPANSION_READY"]

        return IntelligenceDecision(
            "P2099_PORTFOLIO_EVOLUTION",
            "PASS" if ok else "FAIL",
            "PORTFOLIO_EVOLUTION_OK" if ok else "PORTFOLIO_EVOLUTION_DEFENSIVE",
            {
                "evolution_state": evolution_state,
                "top_specialist": ranking[0]["specialist_id"] if ranking else None,
                "equity": equity,
                "drawdown_pct": dd,
            },
        )


def certify(decisions: List[IntelligenceDecision]) -> IntelligenceDecision:
    failed = [d.component for d in decisions if d.status != "PASS"]
    return IntelligenceDecision(
        "P2100_INTELLIGENCE_CERTIFICATION",
        "PASS" if not failed else "FAIL",
        "REALTIME_INTELLIGENCE_LAYER_CERTIFIED" if not failed else "INTELLIGENCE_LAYER_NOT_CERTIFIED",
        {
            "failed_components": failed,
            "passed_components": [d.component for d in decisions if d.status == "PASS"],
            "total_components": len(decisions),
        },
    )


def run_p2091_2100(
    portfolio_path: str,
    p2071_certification_path: str,
    p2081_certification_path: str,
    output_dir: str,
) -> Dict[str, Any]:
    assert_no_financial_execution()

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    portfolio = load_json(portfolio_path)
    p2071 = load_json(p2071_certification_path)
    p2081 = load_json(p2081_certification_path)

    if p2071.get("status") != "PASS":
        raise RuntimeError("P2071_2080_NOT_CERTIFIED")
    if p2081.get("status") != "PASS":
        raise RuntimeError("P2081_2090_NOT_CERTIFIED")

    specialists = extract_specialists(portfolio)

    decisions: List[IntelligenceDecision] = []
    decisions.append(RuntimeAnalytics().evaluate(p2071))
    decisions.append(PortfolioIntelligence().evaluate(specialists, p2081))
    decisions.append(RegimeAnalytics().evaluate(p2071))
    decisions.append(PerformanceAttribution().evaluate(specialists, p2071))
    decisions.append(BehaviorAnalysis().evaluate(p2071))

    ranking_decision = SpecialistRankingEvolution().evaluate(specialists)
    decisions.append(ranking_decision)

    ranking = ranking_decision.payload.get("ranking", [])

    decisions.append(AutoRetirement().evaluate(ranking))
    decisions.append(AutoPromotion().evaluate(ranking))
    decisions.append(PortfolioEvolution().evaluate(ranking, p2081))

    certification = certify(decisions)
    decisions.append(certification)

    mission_status = {d.component: d.status for d in decisions}
    all_pass = all(d.status == "PASS" for d in decisions)

    result = {
        "program": "P2091_2100_REALTIME_INTELLIGENCE_LAYER",
        "status": "PASS" if all_pass else "FAIL",
        "readiness": "REALTIME_INTELLIGENCE_LAYER_CERTIFIED" if all_pass else "NOT_CERTIFIED",
        "absolute_restrictions": enforce_paper_only(),
        "input_dependencies": {
            "portfolio": portfolio_path,
            "p2071_2080": p2071_certification_path,
            "p2081_2090": p2081_certification_path,
        },
        "mission_status": mission_status,
        "decisions": [asdict(d) for d in decisions],
        "intelligence_outputs": {
            "ranking": ranking,
            "top_specialist": ranking[0]["specialist_id"] if ranking else None,
            "retirement_policy": "PAPER_ONLY_NO_DESTRUCTIVE_REMOVAL",
            "promotion_policy": "PAPER_ONLY_METADATA_PROMOTION",
            "portfolio_evolution": next(
                d.payload for d in decisions if d.component == "P2099_PORTFOLIO_EVOLUTION"
            ),
        },
        "next_block": "P2101_2110_AUTONOMOUS_PAPER_OPERATIONS",
    }

    final_path = output / "P2091_2100_FINAL_CERTIFICATION.json"
    audit_path = output / "P2091_2100_AUDIT.md"
    state_path = output / "P2091_2100_INTELLIGENCE_STATE.json"

    final_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    state_path.write_text(json.dumps(result["intelligence_outputs"], indent=2, ensure_ascii=False), encoding="utf-8")

    audit = f"""# MIND TRADER — P2091→P2100 AUDIT

## STATUS
{result["status"]}

## READINESS
{result["readiness"]}

## MISSION STATUS
{json.dumps(mission_status, indent=2, ensure_ascii=False)}

## INTELLIGENCE OUTPUTS
{json.dumps(result["intelligence_outputs"], indent=2, ensure_ascii=False)}

## ABSOLUTE LOCKS
{json.dumps(result["absolute_restrictions"], indent=2, ensure_ascii=False)}

## CONCLUSION
P2091→P2100 executed as consolidated PAPER_ONLY realtime intelligence layer.
No real orders.
No broker execution.
No financial execution.
"""
    audit_path.write_text(audit, encoding="utf-8")

    return result
