
from app.runtime.factual_search_handoff import factual_search_handoff, _LAST_STATE

def test_eldora_topic_clears_motorcycle_state():
    _LAST_STATE.clear()
    factual_search_handoff("base","CR250R 2001 pedal partida quero que vc verifique")
    assert _LAST_STATE
    out=factual_search_handoff("Sobre Eldora, devemos melhorar UX.","Sobre Eldora, o que melhorar?")
    assert "Eldora" in out or "UX" in out
    assert not _LAST_STATE

def test_aprofunde_without_factual_state_does_not_force_cr250r():
    _LAST_STATE.clear()
    out=factual_search_handoff("aprofundamento genérico","aprofunde")
    assert "CR250R" not in out
