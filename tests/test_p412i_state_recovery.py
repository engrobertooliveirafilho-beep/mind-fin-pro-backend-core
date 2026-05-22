
from app.runtime.factual_search_handoff import factual_search_handoff

def test_aprofunde_alias_blocks_generic_context_question():
    out=factual_search_handoff("Parece que você está buscando um aprofundamento, mas não ficou claro em que área específica.","aprofunde")
    assert "não ficou claro" not in out.lower()
    assert "contexto" not in out.lower()
    assert len(out) > 30

def test_deepen_recovery_progresses():
    out1=factual_search_handoff("mesma resposta","aprofunde")
    out2=factual_search_handoff("mesma resposta","aprofunde")
    assert out1 != out2
