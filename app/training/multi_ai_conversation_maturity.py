import os,json
PROVIDERS=["OPENAI_API_KEY","ANTHROPIC_API_KEY","GEMINI_API_KEY","DEEPSEEK_API_KEY","MISTRAL_API_KEY","GROQ_API_KEY","COHERE_API_KEY","PERPLEXITY_API_KEY"]
ROLES=["amiga","professor","debatedor","crítico","estudante cansado","usuário irritado","engenheiro técnico","adolescente","usuário emocional","product strategist","mentor"]
def run():
    available=[p for p in PROVIDERS if os.getenv(p)]
    skipped=[p for p in PROVIDERS if not os.getenv(p)]
    return {"mode":"provider_discovery_no_fake_success","available_providers":available,"skipped_providers":skipped,"roles":ROLES,"executed":len(available)>0,"note":"Sem credencial/env, P2 fica plugável e auditado, não simulado como sucesso falso."}
if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
