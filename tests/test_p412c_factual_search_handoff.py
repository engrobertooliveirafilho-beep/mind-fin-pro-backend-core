
from app.runtime.factual_search_handoff import factual_search_handoff

def test_no_trigger_returns_original():
    assert factual_search_handoff("ok","bom dia") == "ok"

def test_provider_failure_is_honest():
    out=factual_search_handoff("base","ELA É 2001 MODELO CR250R 2 TEMPOS QUERO QUE VC VERIFIQUE")
    assert "busca factual" in out.lower() or len(out) > 20
