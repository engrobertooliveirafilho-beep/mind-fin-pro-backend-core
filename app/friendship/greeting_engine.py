def build_greeting(name="Roberto", memory=None):
    memory = memory or {}
    topic = memory.get("topic") or memory.get("materia")
    exam = memory.get("exam") or memory.get("contexto")

    if topic and exam:
        return f"Bom dia, {name}. Você comentou que tem contexto de {topic} {exam}. Quer que eu monte uma revisão rápida de 10 minutos?"
    if topic:
        return f"Bom dia, {name}. Quer revisar {topic} por 10 minutos comigo hoje?"
    if exam:
        return f"Bom dia, {name}. Você comentou que tem contexto {exam}. Quer organizar uma revisão rápida?"

    return f"Bom dia, {name}. Quer que eu te ajude a organizar seus estudos hoje?"

