from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

repl = {
    "execu├º├úo contextual": "execução contextual",
    "evid├¬ncia e pr├│ximo passo": "evidência e próximo passo",
    "pr├ítica": "prática",
    "m├úo": "mão",
    "├ígua": "água",
    "distribui├º├úo": "distribuição",
    "n├¡vel": "nível",
    "c├ómeras": "câmeras",
    "balan├ºa eletr├┤nica": "balança eletrônica",
    "voc├¬": "você",
    "funcion├írio": "funcionário",
    "supervis├úo": "supervisão",
    "manuten├º├úo": "manutenção",
    "emerg├¬ncia": "emergência",
    "├®": "é",
    "come├ºar": "começar",
    "di├írio": "diário",
    "alimenta├º├úo": "alimentação",
    "semi autom├ítica": "semi automática",
    "c├ómbio": "câmbio",
    "equipamento agr├¡cola": "equipamento agrícola",
    "agr├¡cola": "agrícola",
    "n├úo": "não",
    "est├í": "está",
    "sangria/calibra├º├úo": "sangria/calibração",
    "adapta├º├úo": "adaptação",
    "digita├º├úo": "digitação",
}

for a,b in repl.items():
    s = s.replace(a,b)

p.write_text(s, encoding="utf-8")
