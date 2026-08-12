from app.mind.p5_5c_supabase_ingestion_writer import run_p55c_healthcheck
def test_p55c_healthcheck():
    assert run_p55c_healthcheck()["status"]=="P5.5C_READY"
