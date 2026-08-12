from app.mind.p5_5o_audit_endpoint import run_p55o_healthcheck
from app.mind.p5_5o_audit_endpoint.routes import TABLES

def test_p55o_healthcheck():
    assert run_p55o_healthcheck()["status"]=="P5.5O_READY"

def test_tables():
    assert "p55a_animals" in TABLES
    assert "p55a_valuation_events" in TABLES
