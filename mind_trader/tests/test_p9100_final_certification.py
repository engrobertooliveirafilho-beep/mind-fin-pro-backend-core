from pathlib import Path
from app.p9_final_certification.engine import certify

def test_p9100_certification_remains_blocked_without_functional_evidence():
    snapshot = certify()["P9_STATE_SNAPSHOT"]
    assert snapshot["STATUS"] == "P9_CERTIFICATION_BLOCKED"
    assert snapshot["MODULES_CERTIFIED"] == []
    assert snapshot["EXPORT_READY"] is False
    assert all(value is False for value in snapshot["FUNCTIONAL_GATES"].values())

def test_p9100_reports_are_written_and_readable():
    import json
    certify()
    snapshot = Path("reports/P9.100_FINAL_CERTIFICATION/P9_STATE_SNAPSHOT.json")
    final = Path("reports/P9.100_FINAL_CERTIFICATION/P9.100_final_certification.json")
    assert snapshot.is_file()
    assert final.is_file()
    assert json.loads(final.read_text(encoding="utf-8"))["P9_STATE_SNAPSHOT"]["STATUS"] == "P9_CERTIFICATION_BLOCKED"

def test_p9100_next_phase_is_remediation_not_promotion():
    snapshot = certify()["P9_STATE_SNAPSHOT"]
    assert snapshot["NEXT_PHASE"] == "P9_FUNCTIONAL_REMEDIATION"
    assert snapshot["PROMOTION"] == "FORBIDDEN_PENDING_FUNCTIONAL_CERTIFICATION"
