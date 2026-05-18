def build_response_strategy(intent, state, memory):
    depth=intent.get("depth_required","medium")
    strategy="executar" if intent.get("intent") in ["project_execution","technical_debug"] else "aprofundar"
    return {"strategy":strategy,"required_sections":["Diagnóstico","Estratégia","Execução","Auditoria"],"depth_level":depth,"must_reference_memory":True,"avoid":["generic_answer","topic_drift","unnecessary_question"]}
