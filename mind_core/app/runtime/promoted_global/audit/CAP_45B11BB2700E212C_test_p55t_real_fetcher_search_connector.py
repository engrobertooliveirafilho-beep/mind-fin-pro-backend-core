from app.mind.p5_5t_real_fetcher_search_connector import run_p55t_healthcheck
from app.mind.p5_5t_real_fetcher_search_connector.connector import h, RealFetcherSearchConnector

def test_p55t_healthcheck():
    assert run_p55t_healthcheck()["status"]=="P5.5T_READY"

def test_hash_stable():
    assert h({"a":1,"b":2}) == h({"b":2,"a":1})

def test_extract_query_without_remote():
    c=RealFetcherSearchConnector(url="https://example.supabase.co", key="fake")
    q=c.extract_query({"source_url":"https://www.google.com/search?q=Bushwacker+PBR","raw_payload":{}})
    assert "Bushwacker" in q
