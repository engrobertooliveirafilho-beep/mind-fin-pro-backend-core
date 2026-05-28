from __future__ import annotations
import re

ROBOTIC_LABEL_RE = re.compile(
    r"(?i)\b("
    r"resposta direta|ação recomendada|memória contextual|resumo\s*/\s*compatibility|"
    r"diagnóstico|estratégia|execução|auditoria|detalhamento|pontos-chave|"
    r"análise:\s*contexto|risco:|compatibility:"
    r")\s*:"
)

GENERIC_FALLBACKS = {
    "vamos seguir pelo ponto real e validar o próximo passo.",
    "vou aprofundar mantendo o mesmo assunto e sem mudar de direção.",
    "vamos aprofundar sem reiniciar a conversa: primeiro isolamos a causa real, depois testamos a hipótese principal e só avançamos com evidência.",
}

SAFE_EMPTY_REPLY = "Não recebi conteúdo suficiente para responder com precisão."

def _strip_robotic_labels(text: str) -> str:
    cleaned = ROBOTIC_LABEL_RE.sub("", text or "").strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def sanitize_final_human_output(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return SAFE_EMPTY_REPLY
    cleaned = _strip_robotic_labels(raw)
    if not cleaned:
        return SAFE_EMPTY_REPLY
    if cleaned.lower() in GENERIC_FALLBACKS:
        return SAFE_EMPTY_REPLY
    return cleaned
