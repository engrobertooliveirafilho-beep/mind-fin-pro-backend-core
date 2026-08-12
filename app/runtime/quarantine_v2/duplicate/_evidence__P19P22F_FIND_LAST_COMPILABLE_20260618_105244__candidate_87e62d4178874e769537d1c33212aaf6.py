from app.api.whatsapp import _p19p9_universal_whatsapp_output_guard

def test_p19p9_universal_guard_blocks_generic_confinement_restart():
    out = _p19p9_universal_whatsapp_output_guard(
        "explique melhor",
        "Para automatizar o confinamento de bois e reduzir a necessidade de funcionários, você pode considerar as seguintes etapas: Sistema de Alimentação Automatizada: Invista em alimentadores automáticos que distribuem ração em horários programados.",
        "como posso automatizar meu confinamento de boi, para não precisar de funcionario?"
    )
    assert "indo mais fundo" in out.lower()
    assert "leitura de cocho" in out.lower()
    assert "invista em alimentadores automáticos" not in out.lower()
