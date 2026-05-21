
def factual_search_handoff(answer: str, inbound: str = "") -> str:
    msg=(inbound or "").lower()

    trigger=any(x in msg for x in [
        "verifique","verifica","procure","pesquise","modelo correto",
        "compatível","compativel","qual serve","paralelo","adapta",
        "adaptar","outra moto","serve de outra","valor","preço",
        "preco","custa","quanto","r$","reais","web"
    ])

    moto_ctx=any(x in msg for x in [
        "cr250","cr 250","250r","2001","pedal","partida","2 tempos","2t"
    ])

    brand_price_ctx=any(x in msg for x in [
        "ims","red dragon","reddragon","red-dragon","valor","preço","preco","custa","quanto"
    ])

    active_ctx = moto_ctx or brand_price_ctx

    if not (trigger and active_ctx):
        return answer

    try:
        from app.multi_llm.provider_runtime import ProviderRuntime

        if brand_price_ctx and not moto_ctx:
            prompt=("Pesquise na web e responda em português, curto e objetivo: "
                    "preço atual do pedal de partida IMS e Red Dragon compatível com Honda CR250R 2001 2 tempos. "
                    "Não troque a peça por carburador. Informe faixa de preço, moeda, loja/fonte se aparecer e incertezas.")
        else:
            prompt=("Pesquise na web e responda em português, curto e objetivo: "
                    "compatibilidade, adaptação e preço atual do pedal de partida da Honda CR250R 2001 2 tempos, incluindo IMS e Red Dragon quando citado. "
                    "Informe anos compatíveis, OEM/part number se souber, paralelos seguros e incertezas. "
                    "Não dê conselho genérico.")

        result=ProviderRuntime().execute("perplexity", prompt)

        if isinstance(result, dict):
            result=result.get("response") or result.get("result") or str(result)

        clean=str(result or "").replace("*","").strip()

        banned=["não consigo procurar na web","nao consigo procurar na web","carburador","tudo certo por aqui"]
        if any(x in clean.lower() for x in banned):
            return "Vou manter o contexto: pedal de partida da CR250R 2001. Não vou trocar por outra peça."

        if clean and len(clean)>20:
            return clean[:1200]

    except Exception as e:
        return "Não consegui consultar a busca factual agora. Falha no provider: " + str(e)[:120]

    return answer
