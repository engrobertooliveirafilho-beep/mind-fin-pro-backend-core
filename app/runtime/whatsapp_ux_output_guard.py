import re

def whatsapp_ux_guard(message: str, answer: str, max_chars: int = 650) -> str:
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
        out = out[:max_chars].rsplit(" ", 1)[0].strip()
        out += ". Digite aprofundar que eu continuo."

    return out or "Recebi. Me diga o objetivo em uma frase."
