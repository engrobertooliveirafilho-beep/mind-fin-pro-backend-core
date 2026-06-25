from app.runtime.digital_twin.contract import CognitiveDigitalTwin, TwinSignal


def build_cognitive_digital_twin(user_id_hash: str, conversation_text: str) -> CognitiveDigitalTwin:
    t = (conversation_text or "").lower()

    twin = CognitiveDigitalTwin(user_id_hash=user_id_hash)

    if any(x in t for x in ["prossiga", "direto", "sem enrolar", "objetivo"]):
        twin.communication_model.append(TwinSignal("tone", "direto_sem_floreio", 0.94, 4))
        twin.decision_model.append(TwinSignal("decision_style", "executar_proximo_passo", 0.91, 3))

    if any(x in t for x in ["auditoria", "evidência", "snapshot", "status", "pass", "blocked"]):
        twin.behavior_model.append(TwinSignal("validation_style", "auditoria_com_evidencia", 0.93, 5))
        twin.learning_model.append(TwinSignal("learning_mode", "diagnostico_patch_validacao", 0.89, 4))

    if any(x in t for x in ["powershell", "comando", "script"]):
        twin.communication_model.append(TwinSignal("format", "explicacao_curta_mais_powershell", 0.96, 6))

    if any(x in t for x in ["lançamento", "vender", "conversão", "marketing"]):
        twin.goal_model.append(TwinSignal("business_goal", "lancar_e_converter", 0.84, 3))

    if any(x in t for x in ["frase pronta", "template", "genérico", "robô"]):
        twin.emotional_model.append(TwinSignal("negative_trigger", "resposta_generica", 0.92, 4))

    if any(x in t for x in ["motor universal", "eldora humana", "whatsapp"]):
        twin.goal_model.append(TwinSignal("product_goal", "eldora_humana_motor_universal", 0.95, 6))

    twin.metadata["source"] = "bope11_runtime_inference"
    return twin
