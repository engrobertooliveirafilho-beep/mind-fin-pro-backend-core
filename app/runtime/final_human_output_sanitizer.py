
from __future__ import annotations
import re

ROBOTIC_LABEL_RE = re.compile(
    r"(?i)\b("
    r"resposta direta|ação recomendada|memória contextual|resumo\s*/\s*compatibility|"
    r"diagnóstico|estratégia|execução|auditoria|detalhamento|pontos-chave|"
    r"análise:\s*contexto|risco:|compatibility:"
    r")\s*:"
)

def sanitize_final_human_output(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return "Vamos seguir pelo ponto real e validar o próximo passo."
    if ROBOTIC_LABEL_RE.search(raw):
        return "Vamos aprofundar sem reiniciar a conversa: primeiro isolamos a causa real, depois testamos a hipótese principal e só avançamos com evidência."
    return raw
