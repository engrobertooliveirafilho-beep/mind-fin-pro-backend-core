import json, random
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1809A_REAL_WALK_FORWARD_ENGINE/p1809a_real_walk_forward_report.json")
OUT = Path("reports/P1809B_MONTE_CARLO_10000_TRADE_SEQUENCE")
REPORT = OUT / "p1809b_monte_carlo_10000_report.json"
DETAIL = OUT / "p1809b_monte_carlo_10000_detail.json"

SIMS = 10000
data = json.loads(SRC.read_text(encoding="utf-8"))
edges = data.get("APPROVED_EDGES", [])

def percentile(values, p):
    values = sorted(values)
    return values[int((len(values)-1) * p)] if values else None

def curve_stats(returns):
    equity = 0
    peak = 0
    max_dd = 0
    loss_streak = 0
    max_loss_streak = 0

    for r in returns:
        equity += r
        peak = max(peak, equity)
        max_dd = min(max_dd, equity - peak)

        if r < 0:
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)
        else:
            loss_streak = 0

    return equity, abs(max_dd), max_loss_streak

def synthetic_trade_returns(edge, stress_cost=0.0):
    returns = []
    for y in edge.get("yearly_real", []):
        trades = int(y.get("trades") or 0)
        wr = float(y.get("win_rate") or 0)
        exp = float(y.get("expectancy") or 0)
        payoff = float(y.get("payoff_ratio") or 1)

        base_loss = abs(exp) if abs(exp) > 0 else 0.001
        win_r = max(base_loss * payoff, 0.0005)
        loss_r = -max(base_loss, 0.0005)

        for _ in range(trades):
            r = win_r if random.random() < wr else loss_r
            returns.append(r - stress_cost)

    return returns

stress_profiles = [
    {"name": "BASE", "cost": 0.00000},
    {"name": "SPREAD_STRESS", "cost": 0.00005},
    {"name": "SLIPPAGE_STRESS", "cost": 0.00010},
    {"name": "DELAY_STRESS", "cost": 0.00015},
    {"name": "EXTREME_EXECUTION_STRESS", "cost": 0.00025}
]

results = []

for edge in edges:
    edge_results = []

    for stress in stress_profiles:
        base_returns = synthetic_trade_returns(edge, stress["cost"])

        sim_total = []
        sim_dd = []
        sim_loss_streak = []

        for _ in range(SIMS):
            sample = random.choices(base_returns, k=len(base_returns))
            total, dd, ls = curve_stats(sample)
            sim_total.append(total)
            sim_dd.append(dd)
            sim_loss_streak.append(ls)

        survival = len([x for x in sim_total if x > 0]) / SIMS
        p05 = percentile(sim_total, 0.05)

        edge_results.append({
            "stress_profile": stress["name"],
            "stress_cost_per_trade": stress["cost"],
            "trades_bootstrapped": len(base_returns),
            "return_p01": round(percentile(sim_total, 0.01), 8),
            "return_p05": round(p05, 8),
            "return_p50": round(percentile(sim_total, 0.50), 8),
            "return_p95": round(percentile(sim_total, 0.95), 8),
            "max_drawdown_p50": round(percentile(sim_dd, 0.50), 8),
            "max_drawdown_p95": round(percentile(sim_dd, 0.95), 8),
            "max_loss_streak_p95": percentile(sim_loss_streak, 0.95),
            "survival_probability": round(survival, 6),
            "pass": survival >= 0.95 and p05 > 0
        })

    base_pass = edge_results[0]["pass"]
    stress_pass_count = len([x for x in edge_results if x["pass"]])

    results.append({
        "edge_id": edge["edge_id"],
        "asset": edge["asset"],
        "timeframe": edge["timeframe"],
        "family": edge["family"],
        "tested_years": edge["tested_years"],
        "yearly_consistency": edge["yearly_consistency"],
        "simulations_per_profile": SIMS,
        "stress_results": edge_results,
        "base_mc_pass": base_pass,
        "stress_profiles_passed": stress_pass_count,
        "mc_10k_final_pass": base_pass and stress_pass_count >= 3,
        "status": "MC_10K_APPROVED" if base_pass and stress_pass_count >= 3 else "MC_10K_REJECTED",
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

approved = [r for r in results if r["mc_10k_final_pass"]]

report = {
    "STATUS": "P1809B_MONTE_CARLO_10000_TRADE_SEQUENCE_COMPLETED",
    "EDGES_INPUT": len(edges),
    "SIMULATIONS_PER_STRESS_PROFILE": SIMS,
    "STRESS_PROFILES": [x["name"] for x in stress_profiles],
    "EDGES_TESTED": len(results),
    "MC_10K_APPROVED": len(approved),
    "MC_10K_REJECTED": len(results) - len(approved),
    "APPROVED_EDGES": approved,
    "NEXT": "P1810_TRADE_DNA_ENGINE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

DETAIL.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
