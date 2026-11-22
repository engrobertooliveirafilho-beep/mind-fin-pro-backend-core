import json
import pytest
from app.runtime.p2091_2100_realtime_intelligence_layer import run_p2091_2100, ABSOLUTE_LOCKS


def test_p2091_rejects_upstream_provenance_mismatch_without_evidence(tmp_path, monkeypatch):
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    portfolio=tmp_path/"portfolio.json"
    p2071=tmp_path/"p2071.json"
    p2081=tmp_path/"p2081.json"
    out=tmp_path/"evidence"
    portfolio.write_text(json.dumps({"specialists":[{"id":"s1"}]}))
    p2071.write_text(json.dumps({"status":"PASS","readiness":"REALTIME_PAPER_RUNTIME_CERTIFIED"}))
    p2081.write_text(json.dumps({"status":"PASS","readiness":"REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED",
        "input_dependencies":{"p2071_2080_certification":"unrelated.json"}}))
    with pytest.raises(RuntimeError, match="UPSTREAM_PROVENANCE_MISMATCH"):
        run_p2091_2100(str(portfolio),str(p2071),str(p2081),str(out))
    assert not out.exists()


def test_p2091_missing_inputs_leave_no_certification_artifacts(tmp_path, monkeypatch):
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    out=tmp_path/"evidence"
    with pytest.raises(FileNotFoundError):
        run_p2091_2100(str(tmp_path/"portfolio"),str(tmp_path/"p2071"),
                       str(tmp_path/"p2081"),str(out))
    assert not out.exists()
