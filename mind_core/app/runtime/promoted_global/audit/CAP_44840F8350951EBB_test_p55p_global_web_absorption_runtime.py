from app.mind.p5_5p_global_web_absorption_runtime import run_p55p_healthcheck
from app.mind.p5_5p_global_web_absorption_runtime.runtime import GlobalWebAbsorptionRuntime

def test_p55p_healthcheck():
    h=run_p55p_healthcheck()
    assert h["status"]=="P5.5P_READY"
    assert h["seed_animals"]>=6

def test_expand_queries_without_remote():
    r=GlobalWebAbsorptionRuntime(url="https://example.supabase.co", key="fake")
    rows=r.expand_queries(["Bushwacker"])
    assert len(rows)>=6
    assert rows[0]["evidence_hash"]
