from app.api.whatsapp import _p19p8_suppress_generic_restart

def test_p19p8_blocks_generic_restart_on_explique_melhor():
    out = _p19p8_suppress_generic_restart(
        "explique melhor",
        "Para automatizar seu confinamento de boi e reduzir a necessidade de funcionários, você pode considerar as seguintes etapas: Sistema de Alimentação Automatizado: Invista em alimentadores automáticos que distribuem ração em horários programados.",
        "como posso automatizar meu confinamento de boi"
    )
    assert "indo mais fundo" in out.lower()
    assert "leitura de cocho" in out.lower()
    assert "invista em alimentadores automáticos" not in out.lower()

def test_p19p8_blocks_generic_restart_on_como_faco():
    out = _p19p8_suppress_generic_restart(
        "como eu faço?",
        "Para automatizar o confinamento de bois, considere os seguintes passos: Sistema de Alimentação Automatizado.",
        "automatizar confinamento de boi"
    )
    assert "dieta sai do silo" in out.lower()
    assert "balança integrada" in out.lower()
