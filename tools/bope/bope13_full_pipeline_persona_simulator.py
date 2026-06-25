import json
from pathlib import Path

from app.runtime.knowledge_providers.legacy_domain_provider import build_domain_knowledge
from app.runtime.knowledge_providers.contract import packet_to_context
from app.runtime.digital_twin.builder import build_cognitive_digital_twin

OUT = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\BOPE-13_FULL_PIPELINE_PERSONA_SIMULATOR_20260625_145758")

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

FORBIDDEN = [
    "contexto:",
    "objetivo:",
    "domain=",
    "intent=",
    "resposta legada",
    "como posso ajudar hoje",
    "me dá só o objetivo",
    "entendi. vou responder",
]


def final_answer_engine(inbound_text, legacy_answer, shadow):
    legacy = str(legacy_answer or "").strip()
    packet = shadow.get("packet") or {}
    domain = packet.get("domain", "")

    if domain in ("", "general"):
        return legacy

    return "structured_ready"


def naturalize(final_answer, shadow):
    packet = shadow.get("packet") or {}
    domain = packet.get("domain", "")
    steps = packet.get("steps") or []
    priorities = packet.get("priorities") or []
    constraints = packet.get("constraints") or []
    warnings = packet.get("warnings") or []

    if domain in ("", "general"):
        return final_answer

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

    return final_answer


def apply_twin_style(answer, persona, inbound_text):
    seed = f"{persona}\n{inbound_text}\n{answer}"
    twin = build_cognitive_digital_twin("sim_" + persona, seed)

    text = answer.strip()
    values = []
    for group in [
        twin.communication_model,
        twin.decision_model,
        twin.emotional_model,
        twin.goal_model,
    ]:
        values.extend([s.value for s in group])

    if "direto_sem_floreio" in values:
        text = text.replace("Contexto:", "").replace("Objetivo:", "").strip()

    if "executar_proximo_passo" in values and "Próximo passo:" not in text:
        text += " Próximo passo: execute a primeira etapa e valide."

    return text, twin


def score_answer(answer):
    lower = answer.lower()
    violations = [x for x in FORBIDDEN if x in lower]

    too_short = len(answer.strip()) < 8
    too_technical = "contexto:" in lower or "objetivo:" in lower or "domain=" in lower
    too_long = len(answer) > 700

    score = 100
    score -= len(violations) * 25
    if too_short: score -= 30
    if too_technical: score -= 25
    if too_long: score -= 10

    return max(score, 0), {
        "violations": violations,
        "too_short": too_short,
        "too_technical": too_technical,
        "too_long": too_long,
    }


rows = []

for persona in PERSONAS:
    for topic in TOPICS:
        packet = build_domain_knowledge(topic)
        shadow = {
            "ok": True,
            "context": packet_to_context(packet),
            "packet": packet.__dict__,
        }

        legacy = "Oi, sou a Eldora." if packet.domain == "general" else "resposta legada simulada"
        final = final_answer_engine(topic, legacy, shadow)
        natural = naturalize(final, shadow)
        styled, twin = apply_twin_style(natural, persona, topic)
        score, flags = score_answer(styled)

        rows.append({
            "persona": persona,
            "topic": topic,
            "domain": packet.domain,
            "intent": packet.intent,
            "answer": styled,
            "score": score,
            "flags": flags,
            "twin_signal_count": (
                len(twin.behavior_model)
                + len(twin.communication_model)
                + len(twin.decision_model)
                + len(twin.learning_model)
                + len(twin.goal_model)
                + len(twin.emotional_model)
            ),
            "pass": score >= 80,
        })

total = len(rows)
passed = sum(1 for r in rows if r["pass"])
failed = total - passed

summary = {
    "mission": "BOPE-13",
    "personas": len(PERSONAS),
    "topics": len(TOPICS),
    "turns": total,
    "passed": passed,
    "failed": failed,
    "pass_rate": round((passed / total) * 100, 2),
    "avg_score": round(sum(r["score"] for r in rows) / total, 2),
}

out = {"summary": summary, "rows": rows}

(OUT / "bope13_result.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

md = []
md.append("# BOPE-13 Full Pipeline Persona Simulator\n")
md.append("## Summary\n")
for k, v in summary.items():
    md.append(f"- **{k}**: {v}")

md.append("\n## Failures\n")
for r in rows:
    if not r["pass"]:
        md.append(f"- persona=`{r['persona']}` topic=`{r['topic']}` score={r['score']} flags={r['flags']} answer=`{r['answer']}`")

(OUT / "BOPE13_REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, indent=2, ensure_ascii=False))

