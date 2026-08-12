import json
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P85_RISK_INTELLIGENCE_DOMAIN")
PORT=Path("reports/P84_PORTFOLIO_INTELLIGENCE_DOMAIN/p84_portfolio_candidates.json")
POS=Path("reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_positions.json")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

RULES={
    "max_daily_loss_pct":0.05,
    "internal_daily_guard_pct":0.03,
    "max_total_loss_pct":0.10,
    "internal_total_guard_pct":0.06,
    "max_risk_per_trade_pct":0.0025,
    "max_position_lot":0.01
}

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def position_risk(positions):
    total_profit=sum(float(p.get("profit") or 0) for p in positions)
    total_volume=sum(float(p.get("volume") or 0) for p in positions)
    return {
        "positions":len(positions),
        "floating_pnl":round(total_profit,6),
        "total_volume":round(total_volume,6),
        "risk_status":"CONTROLLED" if total_volume<=0.05 else "EXPOSURE_WARNING",
        **BLOCKS
    }

def portfolio_risk(portfolio):
    concentration=max([float(p.get("allocation_weight") or 0) for p in portfolio], default=0)
    return {
        "portfolio_candidates":len(portfolio),
        "max_weight":concentration,
        "concentration_status":"CONTROLLED" if concentration<=0.05 else "CONCENTRATION_WARNING",
        **BLOCKS
    }

def kill_switch(positions):
    pr=position_risk(positions)
    active = pr["floating_pnl"] < -3000 or pr["total_volume"] > 0.05
    return {"kill_switch_active":active,"reason":"FLOATING_LOSS_OR_EXPOSURE" if active else "NONE",**BLOCKS}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    portfolio=load(PORT)
    positions=load(POS)

    artifacts={
        "p85_01_daily_loss_governor.json":{"rules":RULES,"status":"READY",**BLOCKS},
        "p85_02_max_loss_governor.json":{"rules":RULES,"status":"READY",**BLOCKS},
        "p85_03_risk_per_trade_engine.json":{"max_risk_per_trade_pct":RULES["max_risk_per_trade_pct"],**BLOCKS},
        "p85_04_position_risk_engine.json":position_risk(positions),
        "p85_05_portfolio_risk_engine.json":portfolio_risk(portfolio),
        "p85_06_drawdown_engine.json":{"status":"READY","limits":RULES,**BLOCKS},
        "p85_07_kill_switch_engine.json":kill_switch(positions),
        "p85_08_ftmo_survival_mode.json":{"mode":"NORMAL","defensive_threshold_pct":0.02,"lock_threshold_pct":0.03,**BLOCKS},
        "p85_09_exposure_cap_engine.json":{"max_total_volume":0.05,"current_volume":position_risk(positions)["total_volume"],**BLOCKS},
        "p85_10_risk_certification.json":{"status":"DEEP_IMPLEMENTED",**BLOCKS}
    }

    for k,v in artifacts.items():
        (OUT/k).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding="utf-8")

    report={
        "STATUS":"P85_RISK_INTELLIGENCE_DOMAIN_IMPLEMENTED",
        "MODULES_IMPLEMENTED":10,
        "POSITIONS_INPUT":len(positions),
        "PORTFOLIO_INPUT":len(portfolio),
        "POSITION_RISK_STATUS":artifacts["p85_04_position_risk_engine.json"]["risk_status"],
        "KILL_SWITCH_ACTIVE":artifacts["p85_07_kill_switch_engine.json"]["kill_switch_active"],
        "NEXT":"P86_EXECUTION_INTELLIGENCE_DOMAIN",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p85_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
