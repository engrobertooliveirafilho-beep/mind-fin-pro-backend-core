from pathlib import Path
from mind_trader.app.validation.adversarial_ai import AdversarialValidationEngine, save_adversarial_report

def good_trade():
    return {"entry":100,"stop":98,"target":104,"risk_amount":500,"open_risk":0,"daily_pnl":0,"total_pnl":0,"daily_trades":1,"loss_streak":0}

def good_regime():
    return {"regime":"TREND_UP","normalized_atr":0.005}

def good_genome():
    return {"genome_id":"abc123","regime":"TREND_UP","edge_claim":"NONE"}

def test_good_trade_passes_adversarial_simulation():
    r=AdversarialValidationEngine().review_trade(good_trade(),good_regime(),good_genome())
    assert r["decision"]=="ALLOW_SIMULATED_TRADE"
    assert r["production"]=="BLOCKED"

def test_no_stop_vetoed():
    t=good_trade(); t["stop"]=None
    r=AdversarialValidationEngine().review_trade(t,good_regime(),good_genome())
    assert r["decision"]=="VETO_TRADE"

def test_regime_mismatch_vetoed():
    g=good_genome(); g["regime"]="RANGE_SIDEWAYS"
    r=AdversarialValidationEngine().review_trade(good_trade(),good_regime(),g)
    assert r["decision"]=="VETO_TRADE"

def test_poor_rr_vetoed():
    t=good_trade(); t["target"]=101
    r=AdversarialValidationEngine().review_trade(t,good_regime(),good_genome())
    assert r["decision"]=="VETO_TRADE"

def test_adverse_daily_limit_vetoed():
    t=good_trade(); t["daily_pnl"]=-4600; t["risk_amount"]=500
    r=AdversarialValidationEngine().review_trade(t,good_regime(),good_genome())
    assert r["decision"]=="VETO_TRADE"

def test_unsupported_edge_claim_vetoed():
    g=good_genome(); g["edge_claim"]="PROVEN_EDGE"
    r=AdversarialValidationEngine().review_trade(good_trade(),good_regime(),g)
    assert r["decision"]=="VETO_TRADE"

def test_save_adversarial_report(tmp_path):
    out=save_adversarial_report({"ok":True},str(tmp_path/"adv.json"))
    assert Path(out).exists()
