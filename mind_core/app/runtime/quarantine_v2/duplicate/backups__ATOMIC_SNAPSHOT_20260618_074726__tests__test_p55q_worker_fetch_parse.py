from app.mind.p5_5q_worker_fetch_parse import run_p55q_healthcheck
from app.mind.p5_5q_worker_fetch_parse.worker import extract_claims

def test_p55q_healthcheck():
    assert run_p55q_healthcheck()["status"]=="P5.5Q_READY"

def test_extract_claims():
    c=extract_claims("Bushwacker 13/6 PBR score 46.25 born 2006 semen pedigree")
    assert "13/6" in c["possible_registry_numbers"]
    assert "2006" in c["possible_years"]
    assert "PBR" in c["possible_platforms"]
