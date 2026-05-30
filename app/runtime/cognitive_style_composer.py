import re

def compose_human_style(message:str, answer:str, ctx:dict|None=None)->str:
    ctx = ctx or {}
    subject = ctx.get("last_subject","")
    domain = ctx.get("last_domain","general")

    text = str(answer or "").strip()

    # limpeza chatbot
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.M)
    text = text.replace("Aqui estão", "")
    text = text.replace("É importante", "")
    text = text.replace("Você deve", "Eu olharia")
    text = re.sub(r'[⚠️✅💰🔧]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # resumir frases
    sentences = re.split(r'(?<=[.!?])\s+', text)
    core = " ".join(sentences[:3]).strip()

    # camada cognitiva genérica
    intro = ""
    practical = ""
    next_step = ""

    if domain == "vehicle_buying" and subject:
        intro = f"Olha, sobre a {subject}: "
        practical = "Eu olharia estado real, manutenção e sinais de gambiarra antes de animar."
        next_step = f"Se quiser, eu posso te falar o que costuma dar dor de cabeça nessa {subject} antes de comprar."

    elif subject:
        intro = f"Sobre {subject}: "

    response = " ".join(
        x for x in [intro + core, practical, next_step]
        if x
    )

    response = re.sub(r'\s+', ' ', response).strip()

    if len(response) > 550:
        response = response[:550].rsplit(" ",1)[0] + "..."

    return response or text
