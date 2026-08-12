from app.api.whatsapp import _p19p9_universal_whatsapp_output_guard

def test_p19p11_fast_return_goes_through_universal_guard():
    out = _p19p9_universal_whatsapp_output_guard(
        "explique melhor",
        "Para automatizar o confinamento de bois e reduzir a necessidade de funcionários, você pode seguir os seguintes passos: Sistema de Alimentação Automatizado: Invista em alimentadores automáticos que distribuem ração em horários programados.",
        "como posso automatizar meu confinamento de boi"
    )
    assert "indo mais fundo" in out.lower()
    assert "leitura de cocho" in out.lower()
    assert "invista em alimentadores automáticos" not in out.lower()
