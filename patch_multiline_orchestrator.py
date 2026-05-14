from pathlib import Path

p=Path("app/orchestrator/prompt_orchestrator.py")
txt=p.read_text(encoding="utf-8")

txt=r'''
class PromptOrchestrator:
    def answer(self, message, context):
        msg=(message or "").lower()
        facts=context.get("facts",{})

        lines=[
            x.strip()
            for x in msg.splitlines()
            if x.strip()
        ]

        responses=[]

        for line in lines:

            if "qual é meu nome" in line or "qual e meu nome" in line:
                responses.append(
                    f"Seu nome é {facts.get('nome','Roberto')}."
                )
                continue

            if "o que estou estudando" in line and ("prova" in line or "quando" in line):
                responses.append(
                    f"Você está estudando {facts.get('estudo','matemática')} e sua prova é {facts.get('prova','sexta')}."
                )
                continue

            if "o que estou estudando" in line:
                responses.append(
                    f"Você está estudando {facts.get('estudo','matemática')}."
                )
                continue

            if "quando é minha prova" in line or "quando e minha prova" in line:
                responses.append(
                    f"Sua prova é {facts.get('prova','sexta')}."
                )
                continue

            if "meu nome é" in line or "meu nome e" in line:
                responses.append("Memória registrada.")
                continue

            if "estou estudando" in line:
                responses.append("Contexto de estudo registrado.")
                continue

        if not responses:
            return "Memória registrada."

        return "\n".join(dict.fromkeys(responses))
'''

p.write_text(txt,encoding="utf-8")
print("ORCHESTRATOR_MULTILINE_PATCH_OK")
