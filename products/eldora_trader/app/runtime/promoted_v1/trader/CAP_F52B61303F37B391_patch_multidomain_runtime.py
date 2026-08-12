from pathlib import Path

path = Path("app/api/whatsapp.py")
src = path.read_text(encoding="utf-8")
original = src

old = '''    if domain != "confinamento_bovino":
        return None
'''

new = '''    if domain == "automotivo":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Vamos direto no diagnóstico. Se desligado as marchas entram e ligado travam, o foco é embreagem, atuador, curso, sangria, fluido ou regulagem. "
                "Primeiro valide se o atuador está movimentando todo o curso. Depois faça sangria correta. Em seguida confira sensor/regulagem. "
                "Só depois pense em trocar peça."
            )
        return None

    if domain == "marketing":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Faça em sequência: defina o público, escolha uma promessa clara, crie 3 ângulos de criativo, rode teste pequeno, corte o pior e escale o melhor. "
                "Não comece pelo layout. Comece pela dor, oferta e primeiro gancho."
            )
        return None

    if domain == "trader":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Execute em PAPER_ONLY. Primeiro rode backtest limpo. Depois valide drawdown, payoff, frequência e estabilidade por ativo. "
                "Se passar, vai para simulação controlada. Nada de LIVE, REAL ou FTMO_REAL antes de certificação."
            )
        return None

    if domain != "confinamento_bovino":
        return None
'''

if old not in src:
    raise RuntimeError("Bloco alvo não encontrado em _p19p19_direct_context_reply")

src = src.replace(old, new, 1)
path.write_text(src, encoding="utf-8")

print({
    "changed": src != original,
    "file": str(path)
})
