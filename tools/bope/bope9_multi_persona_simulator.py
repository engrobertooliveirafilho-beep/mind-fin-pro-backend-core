import json
import random
from pathlib import Path

from app.runtime.knowledge_providers.legacy_domain_provider import build_domain_knowledge
from app.runtime.knowledge_providers.contract import packet_to_context

ROOT = Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core")
OUT = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\BOPE-9_MULTI_PERSONA_CONVERSATION_SIMULATOR_20260625_135428")

PERSONAS = [
    "curioso", "apressado", "desconfiado", "iniciante", "técnico",
    "ansioso", "objetivo", "detalhista", "leigo", "empreendedor",
    "fazendeiro", "mecânico", "gestor", "aluno", "professor",
    "mãe ocupada", "jovem estudante", "investidor", "trader iniciante", "vendedor",
    "social media", "dono de negócio", "motorista", "produtor rural", "consultor",
    "cético", "impaciente", "educado", "confuso", "prático",
    "criativo", "analítico", "conservador", "ousado", "econômico",
    "premium", "iniciante digital", "cliente irritado", "cliente satisfeito", "curioso técnico",
    "fitness iniciante", "atleta amador", "dono de carro antigo", "engenheiro", "advogado",
    "médico", "nutricionista", "agropecuarista", "infoprodutor", "gestor de tráfego"
]

TOPICS = [
    "como automatizar confinamento de boi?",
    "minha Mercedes Classe A não entra ré ligada",
    "quero criar criativo de marketing",
    "validar estratégia trader no paper",
    "quero emagrecer com treino e dieta",
    "quem é você e o que consegue fazer?"
]

FOLLOWUPS = [
    "prossiga",
    "como faço isso na prática?",
    "me dá o próximo passo",
    "não entendi",
    "resuma",
    "aprofunde"
]

FORBIDDEN = [
    "contexto:",
    "objetivo:",
    "domain=",
    "intent=",
    "resposta legada",
    "como posso ajudar hoje",
    "me dá só o objetivo",
    "entendi. vou responder"
]


def bope6_build_final_answer(inbound_text, legacy_answer, shadow):
    legacy = str(legacy_answer or "").strip()
    if not isinstance(shadow, dict) or not shadow.get("ok"):
        return legacy

    packet = shadow.get("packet") or {}
    domain = packet.get("domain", "")
    intent = packet.get("intent", "")
    facts = packet.get("facts") or []
    steps = packet.get("steps") or []
    priorities = packet.get("priorities") or []
    constraints = packet.get("constraints") or []
    warnings = packet.get("warnings") or []

    if domain in ("", "general"):
        return legacy

    parts = []
    if domain: parts.append(f"Contexto: {domain}.")
    if intent: parts.append(f"Objetivo: {intent}.")
    if facts: parts.append("Pontos importantes: " + "; ".join(facts[:3]) + ".")
    if priorities: parts.append("Prioridade: " + "; ".join(priorities[:2]) + ".")
    if steps: parts.append("Próximos passos: " + "; ".join(steps[:6]) + ".")
    if constraints: parts.append("Restrições: " + "; ".join(constraints[:3]) + ".")
    if warnings: parts.append("Atenção: " + "; ".join(warnings[:2]) + ".")
    return " ".join(parts).strip() or legacy


def naturalize(final_answer, shadow):
    raw = str(final_answer or "").strip()
    packet = shadow.get("packet") or {}
    domain = packet.get("domain", "")
    steps = packet.get("steps") or []
    priorities = packet.get("priorities") or []
    constraints = packet.get("constraints") or []
    warnings = packet.get("warnings") or []

    if domain in ("", "general"):
        return raw

    if domain == "agro_confinamento":
        return "Começa pelo trato. Automatiza silo, balança, mistura e distribuição por lote. Depois entra cocho, água e pesagem. Câmera e IA vêm depois, não antes."

    if domain == "automotivo_mercedes_aks":
        step_text = "; ".join(steps[:4])
        warn = warnings[0] if warnings else "não troca peça antes de testar."
        return f"Parece foco no acionamento da embreagem/AKS. Vai na sequência: {step_text}. Atenção: {warn}"

    if domain == "marketing_digital":
        step_text = "; ".join(steps[:5])
        priority = priorities[0] if priorities else "começa pela dor e pela oferta."
        return f"Começa pelo essencial: {priority} Depois executa assim: {step_text}."

    if domain == "trader":
        step_text = "; ".join(steps[:5])
        cons = "; ".join(constraints[:2])
        warn = "; ".join(warnings[:2])
        return f"Modo seguro: {cons}. Primeiro: {step_text}. Atenção: {warn}."

    return raw


def simulate_turn(persona, message, legacy):
    packet = build_domain_knowledge(message)
    shadow = {
        "ok": True,
        "context": packet_to_context(packet),
        "packet": packet.__dict__,
        "reason": "knowledge_provider_ok",
    }
    final = bope6_build_final_answer(message, legacy, shadow)
    natural = naturalize(final, shadow)

    lower = natural.lower()
    violations = [x for x in FORBIDDEN if x in lower]

    return {
        "persona": persona,
        "message": message,
        "domain": packet.domain,
        "intent": packet.intent,
        "legacy_answer": legacy,
        "final_answer": final,
        "natural_answer": natural,
        "violations": violations,
        "pass": len(violations) == 0 and len(natural.strip()) >= 8,
    }


rows = []
random.seed(42)

for persona in PERSONAS:
    for topic in TOPICS:
        legacy = "resposta legada simulada"
        rows.append(simulate_turn(persona, topic, legacy))

        followup = random.choice(FOLLOWUPS)
        rows.append(simulate_turn(persona, followup, "Continua pelo contexto anterior e dá o próximo passo."))

total = len(rows)
passed = sum(1 for r in rows if r["pass"])
failed = total - passed

summary = {
    "mission": "BOPE-9",
    "personas": len(PERSONAS),
    "topics": len(TOPICS),
    "turns": total,
    "passed": passed,
    "failed": failed,
    "pass_rate": round((passed / total) * 100, 2),
}

out = {"summary": summary, "rows": rows}

(OUT / "bope9_simulation_result.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

md = []
md.append("# BOPE-9 Multi Persona Conversation Simulator\n")
md.append("## Summary\n")
for k, v in summary.items():
    md.append(f"- **{k}**: {v}")

md.append("\n## Failures\n")
for r in rows:
    if not r["pass"]:
        md.append(f"- persona=`{r['persona']}` msg=`{r['message']}` violations={r['violations']} answer=`{r['natural_answer']}`")

(OUT / "BOPE9_REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, indent=2, ensure_ascii=False))

