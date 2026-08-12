from app.api.whatsapp import _p19p5_block_agricultural_automotive_contamination

def test_p19p5_whatsapp_blocks_agricultural_contamination():
    out = _p19p5_block_agricultural_automotive_contamination(
        "desligado entra marcha, ligado não entra",
        "Parece problema no sistema de transmissão do seu equipamento agrícola."
    )
    assert "equipamento agrícola" not in out.lower()
    assert "aks" in out.lower() or "embreagem" in out.lower()
    assert "mercedes classe a" in out.lower()
