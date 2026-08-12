from app.runtime.automotive_execution_bias_guard import automotive_execution_bias_guard

def test_p19p_aks_replaces_generic_checklist():
    msg = "classe A semi automatica desligado entra marcha mas ligado fica dura e não tem erro"
    old = "Para resolver, siga estes passos: verifique os códigos e leve ao mecânico."
    out = automotive_execution_bias_guard(msg, old)
    assert "desacoplando" in out.lower()
    assert "atuador aks" in out.lower()
    assert "siga estes passos" not in out.lower()
