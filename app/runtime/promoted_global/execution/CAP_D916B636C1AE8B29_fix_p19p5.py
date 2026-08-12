from pathlib import Path

# 1) Corrigir resposta proibida no automotive_domain_guard.py
g = Path("app/runtime/automotive_domain_guard.py")
s = g.read_text(encoding="utf-8")

s = s.replace(
    "Isso aponta para o acionamento da embreagem/AKS do Mercedes Classe A, não para equipamento agrícola. ",
    "Isso aponta para o acionamento da embreagem/AKS do Mercedes Classe A. "
)

g.write_text(s, encoding="utf-8")


# 2) Corrigir indentação no cognitive_pipeline.py perto do save_message
p = Path("app/runtime/cognitive_pipeline.py")
lines = p.read_text(encoding="utf-8").splitlines()

fixed = []
i = 0
while i < len(lines):
    line = lines[i]

    # Remove bloco P19P5 mal indentado antes do save_message
    if "if suppress_agricultural_contamination:" in line:
        j = i + 1
        while j < len(lines) and (
            "final[\"answer\"] = suppress_agricultural_contamination" in lines[j]
            or lines[j].strip() == ""
        ):
            j += 1
        i = j
        continue

    # Insere bloco corrigido antes do save_message correto
    if 'save_message(user_id, "assistant", final["answer"])' in line:
        indent = line[:len(line) - len(line.lstrip())]
        fixed.append(indent + "if suppress_agricultural_contamination:")
        fixed.append(indent + '    final["answer"] = suppress_agricultural_contamination(message, final.get("answer",""), str(intent))')
        fixed.append(line)
        i += 1
        continue

    fixed.append(line)
    i += 1

p.write_text("\n".join(fixed) + "\n", encoding="utf-8")
