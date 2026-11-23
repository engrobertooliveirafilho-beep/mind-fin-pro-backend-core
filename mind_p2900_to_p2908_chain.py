import json, os, math, hashlib, statistics, datetime, random

from p2905_evolution_gate import classify_specialist

TEMP_ROOT = os.environ["TEMP_ROOT"]
RUN_ID = os.environ["RUN_ID"]

def load(rel):
    p = os.path.join(TEMP_ROOT, rel)
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save(rel, obj):
    p = os.path.join(TEMP_ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return p

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def as_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        for k in ["items","records","data","specialists","survivors","ranking","candidates","edges"]:
            if isinstance(x.get(k), list):
                return x[k]
        return [x]
    return []

def num(v, default=0.0):
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default

def pick(o, keys, default=None):
    if not isinstance(o, dict):
        return default
    for k in keys:
        if k in o:
            return o[k]
    return default

now = datetime.datetime.utcnow().isoformat() + "Z"

windows_raw = load("market_atlas/MIND_MARKET_WINDOWS.json")
ranking_raw = load("tournaments/MIND_GLOBAL_EDGE_TOURNAMENT_RANKING.json")
survivors_raw = load("tournaments/MIND_GLOBAL_EDGE_SURVIVOR_POOL.json")
arsenal_raw = load("specialists/MIND_SPECIALIST_ARSENAL_V1.json")
validation_raw = load("validation/MIND_GLOBAL_EDGE_VALIDATION_REPORT.json")

windows = as_list(windows_raw)
ranking = as_list(ranking_raw)
survivors = as_list(survivors_raw)
arsenal = as_list(arsenal_raw)

if not arsenal:
    raise RuntimeError("SPECIALIST ARSENAL EMPTY — ABORTING")

def specialist_id(s, idx):
    return str(pick(s, ["specialist_id","edge_id","id","candidate_id","name"], f"SPECIALIST_{idx:04d}"))

def symbol(s):
    return str(pick(s, ["symbol","asset","ticker"], "UNKNOWN"))

def timeframe(s):
    return str(pick(s, ["timeframe","tf"], "UNKNOWN"))

def regime(s):
    return str(pick(s, ["regime","market_regime","context_regime"], "UNKNOWN"))

def base_score(s):
    vals = []
    for k in ["score","fitness","quality_score","validation_score","rank_score","edge_score","profit_factor","pf","expectancy"]:
        if isinstance(s, dict) and k in s:
            vals.append(num(s[k], 0))
    if vals:
        return sum(vals) / len(vals)
    return 1.0

# P2900 — Stop/Target/Position Optimizer
optimized = []
for i, s in enumerate(arsenal, 1):
    bs = max(base_score(s), 0.01)
    rg = regime(s).lower()
    sym = symbol(s)
    tf = timeframe(s)

    volatility_factor = 1.0
    if "volatile" in rg or "high" in rg:
        volatility_factor = 1.35
    elif "low" in rg or "range" in rg:
        volatility_factor = 0.85

    stop_r = round(max(0.35, min(2.50, 1.00 * volatility_factor / math.sqrt(abs(bs) + 1))), 4)
    target_r = round(max(0.70, min(5.00, stop_r * (1.45 + min(abs(bs), 3.0) * 0.25))), 4)
    breakeven_r = round(max(0.30, stop_r * 0.85), 4)
    trailing_start_r = round(max(0.80, target_r * 0.55), 4)
    partial_exit_r = round(max(0.70, target_r * 0.45), 4)
    position_risk_pct = round(max(0.10, min(0.75, 0.35 / max(stop_r, 0.35))), 4)

    rec = dict(s) if isinstance(s, dict) else {"raw": s}
    rec.update({
        "specialist_id": specialist_id(s, i),
        "symbol": sym,
        "timeframe": tf,
        "regime": regime(s),
        "p2900_position_model": {
            "mode": "BACKTEST_PAPER_ONLY",
            "stop_r": stop_r,
            "target_r": target_r,
            "breakeven_trigger_r": breakeven_r,
            "trailing_start_r": trailing_start_r,
            "partial_exit_trigger_r": partial_exit_r,
            "partial_exit_size_pct": 50,
            "risk_per_trade_pct": position_risk_pct,
            "mae_proxy_r": round(stop_r * 0.72, 4),
            "mfe_proxy_r": round(target_r * 0.88, 4),
            "payoff_proxy": round(target_r / stop_r, 4)
        }
    })
    optimized.append(rec)

p2900 = {
    "phase": "P2900_STOP_TARGET_AND_POSITION_OPTIMIZER",
    "status": "COMPLETE",
    "mode": "BACKTEST_PAPER_ONLY",
    "created_at": now,
    "specialists": len(optimized),
    "records": optimized
}
save("optimization/MIND_P2900_STOP_TARGET_POSITION_OPTIMIZER.json", p2900)

# P2901 — Prospective Regime Engine
symbols = sorted(set(symbol(s) for s in optimized))
regimes = sorted(set(regime(s) for s in optimized))
regime_map = []
for sym in symbols:
    sym_specs = [s for s in optimized if symbol(s) == sym]
    counts = {}
    for s in sym_specs:
        counts[regime(s)] = counts.get(regime(s), 0) + 1
    dominant = max(counts, key=counts.get) if counts else "UNKNOWN"
    regime_map.append({
        "symbol": sym,
        "dominant_current_regime": dominant,
        "candidate_next_regimes": sorted(counts, key=counts.get, reverse=True)[:3],
        "transition_confidence_proxy": round(min(0.95, 0.45 + len(sym_specs) / max(len(optimized),1)), 4),
        "action": "OBSERVE_ONLY"
    })

p2901 = {
    "phase": "P2901_PROSPECTIVE_REGIME_ENGINE",
    "status": "COMPLETE_OBSERVE_ONLY",
    "mode": "BACKTEST_PAPER_ONLY",
    "created_at": now,
    "regime_projection": regime_map
}
save("regime_forecast/MIND_P2901_PROSPECTIVE_REGIME_ENGINE.json", p2901)

# P2902 — Multi-Timeframe Expansion Readiness
available_tfs = sorted(set(str(pick(w, ["timeframe","tf"], "UNKNOWN")) for w in windows if isinstance(w, dict)))
arsenal_tfs = sorted(set(timeframe(s) for s in optimized))
target_tfs = ["M1","M2","M5","M15","M30","H1","H4","D1"]
tf_matrix = []
for tf in target_tfs:
    has_data = tf in available_tfs
    has_specialist = tf in arsenal_tfs
    tf_matrix.append({
        "timeframe": tf,
        "market_atlas_data_available": has_data,
        "specialist_available": has_specialist,
        "status": "READY" if has_data and has_specialist else ("DATA_ONLY" if has_data else "MISSING_DATA")
    })

p2902 = {
    "phase": "P2902_MULTI_TIMEFRAME_EXPANSION",
    "status": "READINESS_COMPLETE",
    "created_at": now,
    "current_arsenal_timeframes": arsenal_tfs,
    "market_atlas_timeframes": available_tfs,
    "target_timeframe_matrix": tf_matrix,
    "note": "Expansion only where Atlas data exists. No synthetic live execution."
}
save("multi_timeframe/MIND_P2902_MULTI_TIMEFRAME_EXPANSION_READINESS.json", p2902)

# P2903 — Portfolio Opportunity Manager
portfolio = []
for sym in symbols:
    specs = [s for s in optimized if symbol(s) == sym]
    avg_payoff = statistics.mean([s["p2900_position_model"]["payoff_proxy"] for s in specs]) if specs else 0
    avg_risk = statistics.mean([s["p2900_position_model"]["risk_per_trade_pct"] for s in specs]) if specs else 0
    portfolio.append({
        "symbol": sym,
        "specialists": len(specs),
        "avg_payoff_proxy": round(avg_payoff, 4),
        "avg_risk_per_trade_pct": round(avg_risk, 4),
        "day_trade_limit": 3,
        "scalp_limit": 10,
        "swing_allowed": True,
        "allow_no_trade_day": True,
        "priority_score": round(avg_payoff * math.log(len(specs)+1), 4)
    })
portfolio = sorted(portfolio, key=lambda x: x["priority_score"], reverse=True)

p2903 = {
    "phase": "P2903_MULTI_ASSET_PORTFOLIO_OPPORTUNITY_MANAGER",
    "status": "COMPLETE_OBSERVE_ONLY",
    "mode": "BACKTEST_PAPER_ONLY",
    "created_at": now,
    "portfolio_universe": portfolio
}
save("portfolio/MIND_P2903_PORTFOLIO_OPPORTUNITY_MANAGER.json", p2903)

# P2904 — Risk Budget + Prop Firm Compliance
risk_rules = {
    "mode": "PAPER_ONLY",
    "live_real_forbidden": True,
    "max_daily_loss_pct": 4.0,
    "max_total_loss_pct": 8.0,
    "max_risk_per_trade_pct": 0.75,
    "max_open_positions": 3,
    "max_correlated_positions": 2,
    "loss_streak_kill_switch": 3,
    "daily_trade_soft_limit": 10,
    "daily_trade_hard_limit": 20,
    "force_no_trade_allowed": True
}
p2904 = {
    "phase": "P2904_RISK_BUDGET_PROP_FIRM_COMPLIANCE_ENGINE",
    "status": "COMPLETE_LOCKED",
    "created_at": now,
    "rules": risk_rules,
    "compliance_decision": "PAPER_ONLY_APPROVED_REAL_FORBIDDEN"
}
save("risk/MIND_P2904_RISK_BUDGET_PROP_FIRM_COMPLIANCE_ENGINE.json", p2904)

# P2905 — Specialist Arsenal Evolution
evolved = []
for s in optimized:
    payoff = s["p2900_position_model"]["payoff_proxy"]
    risk = s["p2900_position_model"]["risk_per_trade_pct"]
    stability = min(1.0, payoff / max(risk, 0.01) / 10)
    # Proxy-derived metrics are descriptive only; the gate blocks promotion.
    gate = classify_specialist(payoff, stability)
    r = dict(s)
    r["p2905_evolution_status"] = {
        "arsenal_version": "V2_CANDIDATE",
        **gate,
        "stability_proxy": round(stability, 4)
    }
    evolved.append(r)

p2905 = {
    "phase": "P2905_SPECIALIST_ARSENAL_EVOLUTION",
    "status": "COMPLETE",
    "created_at": now,
    "specialists": len(evolved),
    "certified_core": 0,
    "unverified_candidates": len(evolved),
    "watchlist": 0,
    "records": evolved
}
save("specialists/MIND_SPECIALIST_ARSENAL_V2_CANDIDATE.json", p2905)

# P2906 — External Sensors Layer
p2906 = {
    "phase": "P2906_EXTERNAL_SENSORS_LAYER",
    "status": "DESIGN_ONLY_NOT_CERTIFIED",
    "created_at": now,
    "sensors": [
        {"name": "economic_calendar", "status": "PLANNED"},
        {"name": "news", "status": "PLANNED"},
        {"name": "sentiment", "status": "PLANNED"},
        {"name": "correlation", "status": "PLANNED"},
        {"name": "volatility_external", "status": "PLANNED"},
        {"name": "liquidity_volume", "status": "PLANNED"}
    ],
    "execution_permission": "NO_LIVE_EXECUTION"
}
save("external_sensors/MIND_P2906_EXTERNAL_SENSORS_LAYER_DESIGN.json", p2906)

# P2907 — Execution Bridge Certification
p2907 = {
    "phase": "P2907_EXECUTION_BRIDGE_CERTIFICATION",
    "status": "PAPER_BRIDGE_CONTRACT_READY",
    "created_at": now,
    "permissions": {
        "live": "FORBIDDEN",
        "real": "FORBIDDEN",
        "paper": "ALLOWED",
        "backtest": "ALLOWED"
    },
    "required_before_any_bridge": [
        "kill_switch",
        "latency_log",
        "order_audit_log",
        "risk_gate",
        "manual_confirmation",
        "paper_only_lock"
    ]
}
save("execution_bridge/MIND_P2907_EXECUTION_BRIDGE_CERTIFICATION_CONTRACT.json", p2907)

# P2908 — Long Run Certification
p2908 = {
    "phase": "P2908_LONG_RUN_CERTIFICATION",
    "status": "CERTIFICATION_PLAN_READY",
    "created_at": now,
    "required_tests": [
        "walk_forward",
        "out_of_sample",
        "multi_year",
        "multi_asset",
        "monte_carlo",
        "stress_test",
        "regime_shift",
        "drawdown_certification",
        "portfolio_certification"
    ],
    "minimum_gate": {
        "mode": "PAPER_ONLY",
        "min_specialists": len(evolved),
        "max_drawdown_required": "TO_BE_MEASURED",
        "stability_required": "TO_BE_MEASURED",
        "approval_for_real": "FORBIDDEN"
    }
}
save("long_run/MIND_P2908_LONG_RUN_CERTIFICATION_PLAN.json", p2908)

# Canon checkpoint + audit
outputs = []
for root, _, files in os.walk(TEMP_ROOT):
    for fn in files:
        if fn.endswith(".json"):
            p = os.path.join(root, fn)
            outputs.append({
                "file": os.path.relpath(p, TEMP_ROOT).replace("\\","/"),
                "sha256": sha256_file(p),
                "size_bytes": os.path.getsize(p)
            })

audit = {
    "run_id": RUN_ID,
    "created_at": now,
    "phase_chain": "P2900_TO_P2908",
    "status": "COMPLETE",
    "mode": "BACKTEST_PAPER_ONLY",
    "live_real_production": "FORBIDDEN",
    "inputs": {
        "windows": len(windows),
        "ranking": len(ranking),
        "survivors": len(survivors),
        "specialists_v1": len(arsenal)
    },
    "outputs": outputs,
    "summary": {
        "p2900_optimized_specialists": len(optimized),
        "p2901_symbols": len(symbols),
        "p2902_current_timeframes": len(arsenal_tfs),
        "p2903_portfolio_assets": len(portfolio),
        "p2905_core_specialists": p2905["certified_core"],
        "p2905_watchlist": p2905["watchlist"]
    },
    "next_required": "P2908_LONG_RUN_EXECUTION_AND_CERTIFICATION_RUNNER"
}
save("audits/MIND_P2900_TO_P2908_FULL_CHAIN_AUDIT_REPORT.json", audit)

checkpoint = {
    "checkpoint": RUN_ID,
    "created_at": now,
    "current_state": "P2900_TO_P2908_CHAIN_COMPLETE",
    "previous_confirmed": "P2899_GLOBAL_SPECIALIST_ARSENAL_READY",
    "next": "P2908_LONG_RUN_EXECUTION_AND_CERTIFICATION_RUNNER",
    "hard_locks": {
        "BACKTEST": True,
        "PAPER_ONLY": True,
        "LIVE": "FORBIDDEN",
        "REAL": "FORBIDDEN",
        "PRODUCTION": "FORBIDDEN"
    },
    "canonical_outputs": outputs
}
save("checkpoints/MIND_P2900_TO_P2908_FULL_CHAIN_CHECKPOINT.json", checkpoint)

print("============================================================")
print("P2900 TO P2908 FULL CHAIN COMPLETE")
print("STATUS........ COMPLETE")
print(f"SPECIALISTS... {len(optimized)}")
print(f"SYMBOLS....... {len(symbols)}")
print(f"TIMEFRAMES.... {len(arsenal_tfs)}")
print(f"PORTFOLIO..... {len(portfolio)}")
print(f"CORE SPECS.... {p2905['certified_core']}")
print(f"WATCHLIST..... {p2905['watchlist']}")
print("LIVE/REAL..... FORBIDDEN")
print("NEXT.......... P2908_LONG_RUN_EXECUTION_AND_CERTIFICATION_RUNNER")
print("============================================================")
  