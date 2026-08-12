from app.runtime.p19p3_safe_runtime_hook import p19p3_safe_runtime_hook

def test_p19p3_aks_specific():
    r = p19p3_safe_runtime_hook("desligado entra todas as marchas, ligado fica dura")
    assert r is not None
    assert "AKS" in r or "embreagem" in r
    assert "câmbio interno" in r or "acionamento" in r

def test_p19p3_link_piece_context():
    r = p19p3_safe_runtime_hook("me envia o link", "Mercedes Classe A atuador AKS peça")
    assert r is not None
    assert "peça" in r
    assert "carro" not in r.lower() or "não do carro" in r.lower()

def test_p19p3_typo_context():
    r = p19p3_safe_runtime_hook("nao entnedeu?")
    assert r is not None
    assert "contexto anterior" in r

def test_p19p3_followup_context():
    r = p19p3_safe_runtime_hook("aprofunde", "comparação anterior sobre peça Mercedes")
    assert r is not None
    assert "contexto anterior" in r

def test_p19p3_compare():
    r = p19p3_safe_runtime_hook("compare com outros países")
    assert r is not None
    assert "Comparação objetiva" in r

def test_p19p3_fallback_none():
    assert p19p3_safe_runtime_hook("bom dia") is None
