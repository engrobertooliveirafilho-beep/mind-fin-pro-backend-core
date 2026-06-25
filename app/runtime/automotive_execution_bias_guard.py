def automotive_execution_bias_guard(user_message: str, answer: str) -> str:
    msg = (user_message or "").lower()
    ans = (answer or "").lower()

    is_aks = any(x in msg for x in ["aks", "classe a", "semi automatica", "semi automática"])
    symptom = (
        ("desligado" in msg and "marcha" in msg)
        or ("ligado" in msg and "dura" in msg)
        or ("não tem erro" in msg or "nao tem erro" in msg)
    )

    generic = any(x in ans for x in [
        "siga estes passos",
        "verifique os códigos",
        "anote os sintomas",
        "leve o carro",
        "mecânico especializado",
        "diagnóstico do problema"
    ])

    if is_aks or symptom or generic:
        return (
            "Pelo sintoma, o foco não é scanner: se desligado entra marcha e ligado fica duro, "
            "a embreagem provavelmente não está desacoplando totalmente. No Classe A semi-automático, "
            "eu verificaria primeiro o curso do atuador AKS, a haste, o garfo/rolamento e a adaptação do AKS. "
            "O atuador mexe a haste quando liga a ignição?"
        )

    return answer
