def score_response(text: str) -> dict:
    t=(text or "").strip()
    score=100
    flags=[]
    bad=["não entendi","frase genérica","fallback","não ficou bom","ainda estamos ajustando"]
    if len(t) < 20:
        score-=25; flags.append("too_short")
    if any(x in t.lower() for x in bad):
        score-=20; flags.append("fallback_language")
    if not any(x in t.lower() for x in ["diagnóstico","estratégia","execução","auditoria","próximo","resolver","contexto"]):
        score-=10; flags.append("low_operational_structure")
    return {"score": max(0, min(100, score)), "flags": flags}
