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

    out = out.replace("**", "").replace("#", "")
    out = out.replace("equals", "é igual a").replace("Here are", "Aqui vão")
    out = re.sub(r"\s+", " ", out).strip()

    if len(out) > max_chars:
        cut = out[:max_chars]
        out = cut.rsplit(".", 1)[0].strip() or cut.rsplit(" ", 1)[0].strip()
        out += "."

    return out or "Recebi. Me diga o objetivo em uma frase."
