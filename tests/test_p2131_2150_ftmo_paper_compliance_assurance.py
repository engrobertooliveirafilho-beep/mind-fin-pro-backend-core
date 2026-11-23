from app.runtime.p2131_2150_ftmo_paper_compliance_assurance import run_p2131_2150, enforce, assert_locks


def test_p2131_2150_locks():
    locks = enforce()
    assert locks["MIND_MODE"] == "PAPER_ONLY"
    assert locks["REAL_ORDERS"] == "FORBIDDEN"
    assert locks["BROKER_EXECUTION"] == "DISABLED"
    assert locks["FINANCIAL_EXECUTION"] == "DISABLED"
    assert locks["FTMO_REAL"] == "FORBIDDEN"
    assert_locks()


def test_p2131_2150_certification(tmp_path):
    r = run_p2131_2150(str(tmp_path))
    assert r["status"] == "PASS"
    assert r["readiness"] == "FTMO_PAPER_COMPLIANCE_AND_OPERATIONAL_ASSURANCE_CERTIFIED"
    assert r["mission_status"]["P2140_FTMO_PAPER_COMPLIANCE_CERTIFICATION"] == "PASS"
    assert r["mission_status"]["P2150_OPERATIONAL_READINESS_CERTIFICATION"] == "PASS"
    assert r["absolute_restrictions"]["REAL_ORDERS"] == "FORBIDDEN"
    assert r["absolute_restrictions"]["BROKER_EXECUTION"] == "DISABLED"
    assert r["absolute_restrictions"]["FINANCIAL_EXECUTION"] == "DISABLED"
