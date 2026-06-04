
from app.runtime.whatsapp_ux_output_guard import whatsapp_ux_guard

def test_blocks_money_placeholder():
    r=whatsapp_ux_guard("preço?","Faixa de preço R$ 000 a R$ 000.")
    assert "Não vou chutar número" in r

def test_blocks_km_placeholder():
    r=whatsapp_ux_guard("manutenção?","Manutenção a cada 000 km.")
    assert "Não vou chutar número" in r
