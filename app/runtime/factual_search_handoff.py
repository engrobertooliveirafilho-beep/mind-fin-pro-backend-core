
def factual_search_handoff(answer: str, inbound: str = "") -> str:
    msg=(inbound or "").lower()
    trigger=any(x in msg for x in ["verifique","verifica","procure","pesquise","modelo correto","compatível","compativel","qual serve","paralelo","adapta","adaptar","outra moto","serve de outra"])
    moto=any(x in msg for x in ["cr250","cr 250","250r","2001","pedal","partida","2 tempos","2t"])

    if not (trigger and moto):
        return answer

    try:
        from app.multi_llm.provider_runtime import ProviderRuntime
        prompt=("Pesquise e responda em português, curto e objetivo: "
                "compatibilidade do pedal de partida da Honda CR250R 2001 2 tempos. "
                "Informe anos compatíveis, OEM/part number se souber, paralelos seguros e incertezas. "
                "Não dê conselho genérico.")
        result=ProviderRuntime().execute("perplexity", prompt)
        if isinstance(result, dict):
            result = result.get("response") or result.get("result") or str(result)
        clean = str(result or '').replace('*','').strip()
        if clean and len(clean) > 20:
            return clean[:1200]
    except Exception as e:
        return "Não consegui consultar a busca factual agora. Falha no provider: " + str(e)[:120]

    return answer
