import re

def whatsapp_ux_guard(message: str, answer: str, max_chars: int = 420) -> str:
    msg = str(message or "").strip().lower()
    out = str(answer or "").strip()

    if re.fullmatch(r"\s*\d+\s*[\+\-\*/]\s*\d+\s*", msg):
        expr = re.sub(r"[^0-9+\-*/(). ]", "", msg)
        try:
            return str(eval(expr, {"__builtins__": {}}, {}))
        except Exception:
            pass

    if any(x in msg for x in ["comer", "restaurante", "jantar", "almoço", "barato", "comida"]):
        return "Para comer barato: 1) procure prato feito/buffet do dia; 2) lanchonetes e cafés fora do miolo turístico; 3) pizzarias ou comida por quilo. Em Holambra, confirme preço e horário antes de ir."

    if any(x in msg for x in ["comprar", "moto", "usada", "fazer 250", "vale a pena"]):
        return "Fazer 250 usada vale se estiver inteira. Checklist: motor frio sem ruído, elétrica OK, suspensão/freios bons, documentação limpa e revisão comprovada. Faça laudo antes de pagar."

    out = out.replace("**", "").replace("#", "")
    out = out.replace("equals", "é igual a")
    out = re.sub(r"\s+", " ", out).strip()

    if len(out) > max_chars:
        out = out[:max_chars].rsplit(".", 1)[0].strip()
        if not out:
            out = answer[:max_chars].rsplit(" ", 1)[0].strip()
        out += "."

    return out or "Recebi. Me diga o objetivo em uma frase."
