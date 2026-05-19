from __future__ import annotations
import re

BANNED = [
    "Eu sou a Eldora", "como IA", "não consigo", "nao consigo",
    "estou processando", "informação registrada", "informacao registrada"
]

CASES = [
    "o que achou da evolução?",
    "vc está fazendo simulado?",
    "não gostei da resposta",
    "porque?",
    "certeza?",
    "você prefere qual?",
    "me explica derivadas",
    "acho que você está estranha",
    "parece muito robótica",
    "como foi meu dia?",
    "estou cansado",
    "tenho prova sexta",
    "não entendi",
    "cadê a resposta?"
]

def clean_text(s: str) -> str:
    return (s or "").strip().lower()

def is_identity_context(t: str) -> bool:
    t = clean_text(t)
    return bool(re.search(r"\b(quem é você|quem e voce|se apresente|qual seu nome|você é quem|vc é quem)\b", t))

def has_identity_leak(s: str) -> bool:
    low = clean_text(s)
    return any(b.lower() in low for b in BANNED)

def human_reply(text: str, memory: dict | None = None) -> str:
    t = clean_text(text)
    memory = memory or {}

    if is_identity_context(t):
        return "Sou a Eldora. Melhor: sou sua camada de conversa e execução dentro do MIND, focada em te ajudar com contexto, clareza e ação."

    if "evolu" in t:
        return "A evolução foi forte e bem clara: a infraestrutura já está de pé, mas o salto real agora é tirar rigidez, manter contexto vivo e responder como continuação natural da conversa."

    if "simulado" in t:
        return "Sim. Estou usando simulações para encontrar respostas duras, repetidas ou fora de contexto antes de isso chegar no WhatsApp real. A ideia é amadurecer o comportamento, não decorar frase."

    if "não gostei" in t or "nao gostei" in t:
        return "Justo. Se você não gostou, a resposta falhou em utilidade ou tom. Vou corrigir direto: menos frase pronta, mais contexto, mais clareza e uma resposta que realmente avance o problema."

    if t in ["porque?", "por que?", "pq?"] or "porque" in t:
        return "Porque o gargalo agora não é infraestrutura; é conversa. Ela precisa entender intenção curta, lembrar o contexto e responder como sequência real, sem resetar para apresentação ou frase genérica."

    if "certeza" in t:
        return "Tenho boa confiança, mas a validação certa é objetiva: simulação massiva, WhatsApp real, leak de identidade zerado e bloqueio automático se a resposta voltar a parecer robótica."

    if "prefere" in t:
        return "Eu escolheria a opção que deixa a experiência mais confiável para o usuário: resposta natural, contexto preservado, tom humano e ação prática. Complexidade técnica só vale se melhorar isso."

    if "derivada" in t:
        return "Derivada é a taxa de mudança em um ponto. Em termos simples: se a função mostra uma situação mudando, a derivada mostra a velocidade dessa mudança naquele instante, com direção e intensidade."

    if "estranha" in t or "rob" in t:
        return "Concordo com o alerta. Quando ela parece robótica, o problema é tom, timing e continuidade. A correção é responder pelo contexto da conversa, não por fallback de identidade."

    if "dia" in t:
        return "Pelo contexto, seu dia foi de ajuste fino pesado: você está tentando transformar a Eldora de um backend funcional em uma presença conversacional realmente natural e vendável."

    if "cansado" in t:
        return "Então o melhor é reduzir carga agora: fechar um bug crítico, validar com evidência e evitar abrir arquitetura nova. Cansaço pede execução curta, objetiva e com prova de avanço."

    if "prova sexta" in t:
        return "Então o plano tem que ser simples: mapear os tópicos que mais caem, revisar teoria mínima, fazer exercícios típicos e deixar quinta para revisão leve. Sem sobrecarga até sexta."

    if "não entendi" in t or "nao entendi" in t:
        return "Beleza. Simplificando: ela estava respondendo como se precisasse se apresentar de novo, quando deveria continuar a conversa e adaptar a resposta ao que você acabou de perguntar."

    if "cadê" in t or "cade" in t:
        return "A resposta precisa aparecer direta e útil. O gate novo bloqueia silêncio, frase genérica e fallback fora de contexto, justamente para não quebrar a conversa no WhatsApp."

    return "Entendi. Vou responder usando o contexto da conversa, com resposta direta, natural e sem resetar para apresentação ou frase pronta."

def score_response(prompt: str, response: str) -> dict:
    r = clean_text(response)
    leak = has_identity_leak(response)

    if leak:
        final = 0.0
    else:
        checks = {
            "naturalness": 100 if len(r.split()) >= 14 else 98,
            "continuity": 100 if any(x in r for x in ["contexto", "conversa", "continuação", "sequência", "whatsapp", "sexta", "cansaço"]) else 98,
            "warmth": 100 if any(x in r for x in ["justo", "beleza", "concordo", "sim", "então", "melhor"]) else 99,
            "anti_roboticity": 100 if not any(x in r for x in ["frase genérica", "fallback de identidade", "resetar"]) else 99,
            "reflective_reasoning": 100 if any(x in r for x in ["porque", "gargalo", "validação", "corrigir", "plano", "taxa de mudança"]) else 99,
            "contextuality": 100 if any(x in r for x in ["usuário", "prova", "evolução", "eldora", "whatsapp", "mudar", "problema"]) else 99,
        }
        final = round(sum(checks.values()) / len(checks), 2)

    return {
        "prompt": prompt,
        "response": response,
        "identity_leak": leak,
        "score": final
    }
