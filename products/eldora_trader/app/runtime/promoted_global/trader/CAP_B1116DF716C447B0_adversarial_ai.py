import json
from pathlib import Path

class DefenderAgent:
    def review(self, trade, regime_report, genome):
        reasons=[]
        if trade.get("risk_amount",0) <= 0: reasons.append("INVALID_RISK")
        if trade.get("stop") is None: reasons.append("NO_STOP")
        if regime_report.get("regime") != genome.get("regime"): reasons.append("REGIME_GENOME_MISMATCH")
        passed=not reasons
        return {"agent":"DEFENDER","passed":passed,"reasons":reasons or ["TRADE_HAS_BASIC_SUPPORT"]}

class AttackerAgent:
    def review(self, trade, regime_report, genome):
        reasons=[]
        rr=abs((trade.get("target",0)-trade.get("entry",0)) / (trade.get("entry",1)-trade.get("stop",trade.get("entry",1)))) if trade.get("stop") is not None and trade.get("entry") != trade.get("stop") else 0
        if rr < 1.2: reasons.append("POOR_RISK_REWARD")
        if regime_report.get("regime") in ["MIXED_TRANSITION","UNDEFINED"]: reasons.append("WEAK_OR_UNDEFINED_REGIME")
        if trade.get("loss_streak",0) >= 2: reasons.append("LOSS_STREAK_CONTEXT")
        passed=not reasons
        return {"agent":"ATTACKER","passed":passed,"reasons":reasons or ["NO_MAJOR_ATTACK_FOUND"]}

class FailureHunterAgent:
    def review(self, trade, regime_report, genome):
        reasons=[]
        if not genome.get("genome_id"): reasons.append("GENOME_ID_MISSING")
        if genome.get("edge_claim") not in ["NONE","NONE_UNTIL_PAPER_AND_LIVE_EVIDENCE"]: reasons.append("UNSUPPORTED_EDGE_CLAIM")
        if trade.get("daily_trades",0) > 5: reasons.append("OVERTRADING_RISK")
        if trade.get("open_risk",0) + trade.get("risk_amount",0) > 2000: reasons.append("AGGREGATED_RISK_TOO_HIGH")
        passed=not reasons
        return {"agent":"FAILURE_HUNTER","passed":passed,"reasons":reasons or ["NO_STRUCTURAL_FAILURE_FOUND"]}

class AdverseScenarioAgent:
    def review(self, trade, regime_report, genome):
        reasons=[]
        risk=float(trade.get("risk_amount",0))
        daily_pnl=float(trade.get("daily_pnl",0))
        total_pnl=float(trade.get("total_pnl",0))
        simulated_slippage_loss=risk*1.25
        if abs(daily_pnl) + simulated_slippage_loss > 5000: reasons.append("ADVERSE_DAILY_LIMIT_BREACH")
        if abs(total_pnl) + simulated_slippage_loss > 10000: reasons.append("ADVERSE_TOTAL_LIMIT_BREACH")
        if regime_report.get("normalized_atr",0) > 0.02: reasons.append("EXTREME_VOLATILITY")
        passed=not reasons
        return {"agent":"ADVERSE_SCENARIO","passed":passed,"reasons":reasons or ["SURVIVED_BASIC_ADVERSE_SCENARIO"]}

class AdversarialValidationEngine:
    def __init__(self):
        self.agents=[DefenderAgent(),AttackerAgent(),FailureHunterAgent(),AdverseScenarioAgent()]

    def review_trade(self, trade, regime_report, genome):
        reviews=[a.review(trade,regime_report,genome) for a in self.agents]
        passed=all(r["passed"] for r in reviews)
        return {
            "adversarial_passed":passed,
            "decision":"ALLOW_SIMULATED_TRADE" if passed else "VETO_TRADE",
            "reviews":reviews,
            "production":"BLOCKED",
            "edge_claim":"NONE"
        }

def save_adversarial_report(report,path="mind_trader/reports/P8.33_adversarial_report.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
