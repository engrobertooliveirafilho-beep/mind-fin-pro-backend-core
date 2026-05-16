def build_greeting(name="Roberto", memory=None):
    topic=(memory or {}).get("study_topic")
    if topic: return f"Bom dia, {name}. Quer revisar {topic} por 10 min comigo hoje?"
    return f"Bom dia, {name}. Quer que eu te ajude a organizar seus estudos hoje?"
def encouragement(): return "Você não precisa resolver tudo agora. Escolhe uma coisa pequena e eu te ajudo a destravar."
