import pytest
from decimal import Decimal
from app.runtime.p2301_cost_stress_audit import reconcile_stress

def fixture():
    rows=[]
    refs={}
    for family in ("LIQUIDITY_SWEEP_REVERSAL","VWAP_REVERSION"):
        for confirmation in ("MTF_REQUIRED","VOLATILITY_REQUIRED"):
            base=Decimal("15838") if (family,confirmation)==("LIQUIDITY_SWEEP_REVERSAL","MTF_REQUIRED") else Decimal("15212")
            refs[(family,confirmation)]="1.5838" if base==15838 else "1.5212"
            for spread in (1,2,3):
                for slippage in ("LIGHT","MEDIUM","AGGRESSIVE"):
                    scenario=f"SPREAD_X{spread}_SLIPPAGE_{slippage}"
                    penalty=Decimal("0.035")*spread+Decimal("0.02")
                    rows.append(dict(symbol="GER40",timeframe="H1",family=family,confirmation=confirmation,exit_model="TIME_EXIT",mode="PAPER_ONLY",real_orders="FORBIDDEN",scenario=scenario,base_pf_p10=str(base),total_penalty=str(penalty),adjusted_pf=str(base-penalty)))
    return rows,refs

def test_historical_scale_mismatch_blocks_certification():
    rows,refs=fixture()
    result=reconcile_stress(rows,refs)
    assert result["affected_rows"]==36
    assert result["historical_passes_certified"]==0
    assert not result["promotion_allowed"]

def test_corrected_baseline_still_requires_trade_replay():
    rows,refs=fixture()
    for row in rows:
        row["base_pf_p10"]=refs[(row["family"],row["confirmation"])]
        row["adjusted_pf"]=str(Decimal(row["base_pf_p10"])-Decimal(row["total_penalty"]))
    result=reconcile_stress(rows,refs)
    assert result["status"]=="BASELINE_RECONCILED_REPLAY_REQUIRED"
    assert not result["e2e_certified"]

@pytest.mark.parametrize("key,bad",[
    ("mode","LIVE"),("real_orders","ALLOWED"),("base_pf_p10","NaN"),
    ("total_penalty","-1"),("adjusted_pf","inf"),("symbol","EURUSD"),
])
def test_fail_closed(key,bad):
    rows,refs=fixture()
    rows[0][key]=bad
    with pytest.raises(ValueError):reconcile_stress(rows,refs)

def test_incomplete_scenarios_rejected():
    rows,refs=fixture()
    with pytest.raises(ValueError):reconcile_stress(rows[:-1],refs)

def test_arithmetic_mismatch_rejected():
    rows,refs=fixture()
    rows[0]["adjusted_pf"]="0"
    with pytest.raises(ValueError,match="P2301_ARITHMETIC_MISMATCH"):reconcile_stress(rows,refs)
