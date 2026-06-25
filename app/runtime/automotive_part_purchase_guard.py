def automotive_part_purchase_guard(user_message: str, answer: str, context: str = "") -> str:
    msg = (user_message or "").lower()
    ctx = (context or "").lower()
    ans = (answer or "").lower()

    wants_link = any(x in msg for x in ["link", "comprar", "me envia", "me mande"])
    aks_context = any(x in (msg + " " + ctx + " " + ans) for x in [
        "atuador aks", "aks", "classe a", "semi automatica", "semi automática"
    ])

    wrong_vehicle_purchase = any(x in ans for x in [
        "comprar um veículo", "tipo de carro", "carro que você está interessado"
    ])

    if wants_link and aks_context:
        return (
            "Você quer comprar o atuador AKS do Mercedes Classe A 2000, não o carro. "
            "Procure por: 'atuador AKS Mercedes Classe A W168 semi automático'. "
            "Antes de comprar, confirme código da peça, aplicação W168, conector, estado da haste e garantia."
        )

    if wrong_vehicle_purchase and aks_context:
        return (
            "Corrigindo: o contexto é peça, não veículo. "
            "O item é o atuador AKS do Mercedes Classe A W168 semi automático."
        )

    return answer
