from app.runtime.automotive_part_purchase_guard import automotive_part_purchase_guard

def test_p19p2_purchase_link_preserves_aks_part_context():
    out = automotive_part_purchase_guard(
        "me envia o link para eu comprar",
        "Para ajudá-lo a comprar um veículo, preciso de mais informações.",
        "Mercedes Classe A 2000 atuador AKS semi automática"
    )
    assert "atuador AKS" in out
    assert "não o carro" in out
    assert "comprar um veículo" not in out
