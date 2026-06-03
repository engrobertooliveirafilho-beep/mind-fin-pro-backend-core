def route_natural_whatsapp(message):
    msg=(message or "").lower().strip()
    if any(x in msg for x in ["qual seu nome","quem é vc","quem e vc","quem é você","quem e voce","como vc chama","como você chama"]):
        return None
    if msg in ["aprofunde","aprofundar"]:
        return None
    if msg in ["bom dia","boa tarde","boa noite","oi","olá","ola","eu tô bem","eu to bem"]:
        return None
    return None


