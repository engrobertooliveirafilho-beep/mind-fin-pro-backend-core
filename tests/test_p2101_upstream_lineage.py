import json
import pytest
from app.runtime.p2101_2110_autonomous_paper_operations import run_p2101_2110, ABSOLUTE_LOCKS


@pytest.mark.parametrize("tamper", ["p2081_link","p2091_link","p2091_readiness"])
def test_p2101_rejects_false_upstream_chain_without_artifacts(tmp_path, monkeypatch, tamper):
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    portfolio=tmp_path/"portfolio.json"
    p2071=tmp_path/"p2071.json"
    p2081=tmp_path/"p2081.json"
    p2091=tmp_path/"p2091.json"
    out=tmp_path/"evidence"
    portfolio.write_text(json.dumps({"specialists":[{"id":"s1"}]}))
    p2071.write_text(json.dumps({"status":"PASS","readiness":"REALTIME_PAPER_RUNTIME_CERTIFIED"}))
    doc2081={"status":"PASS","readiness":"REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED",
             "input_dependencies":{"p2071_2080_certification":str(p2071)}}
    doc2091={"status":"PASS","readiness":"REALTIME_INTELLIGENCE_LAYER_CERTIFIED",
             "input_dependencies":{"p2071_2080":str(p2071),"p2081_2090":str(p2081)}}
    if tamper=="p2081_link":
        doc2081["input_dependencies"]["p2071_2080_certification"]="unrelated"
    elif tamper=="p2091_link":
        doc2091["input_dependencies"]["p2081_2090"]="unrelated"
    else:
        doc2091["readiness"]="NOT_CERTIFIED"
    p2081.write_text(json.dumps(doc2081))
    p2091.write_text(json.dumps(doc2091))
    with pytest.raises(RuntimeError, match="UPSTREAM"):
        run_p2101_2110(str(portfolio),str(p2071),str(p2081),str(p2091),str(out))
    assert not out.exists()

def test_simulated_recovery_cannot_be_reported_as_healed(monkeypatch):
    from app.runtime.p2101_2110_autonomous_paper_operations import (
        AutoRecovery, AutoRestart, AutoHealing,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    recovery=AutoRecovery().evaluate({"runtime_status":"FAULTED","heartbeat":0,"recovery_count":0})
    restart=AutoRestart().evaluate(recovery.payload["recovered"])
    assert recovery.status == "FAIL"
    assert restart.status == "FAIL"
    healing=AutoHealing().evaluate({"locks_valid":True,
        "recovery_executed":recovery.status=="PASS",
        "restart_executed":restart.status=="PASS"})
    assert healing.status == "FAIL"
    assert "HEAL_RECOVERY_EXECUTED" in healing.payload["healing_actions"]
    assert "HEAL_RESTART_EXECUTED" in healing.payload["healing_actions"]
