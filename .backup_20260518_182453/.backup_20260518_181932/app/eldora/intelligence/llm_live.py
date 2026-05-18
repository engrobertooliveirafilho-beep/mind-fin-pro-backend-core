import os

def select_model_by_cost(intent: str = "general") -> dict:
    return {
        "provider": "openai" if os.getenv("OPENAI_API_KEY") else "fallback",
        "model": os.getenv("ELDORA_LLM_MODEL", "gpt-4o-mini"),
        "max_tokens": int(os.getenv("ELDORA_LLM_MAX_TOKENS", "400")),
        "llm_real_available": bool(os.getenv("OPENAI_API_KEY")),
    }

def fallback_model(prompt: str, context: str = "") -> dict:
    return {
        "answer": "Fallback Eldora ativo. Sem OPENAI_API_KEY validada no runtime.",
        "llm_real_used": False,
        "cost_controlled": True,
    }

def generate_llm_response(prompt: str, context: str = "", intent: str = "general") -> dict:
    cfg = select_model_by_cost(intent)
    if not cfg["llm_real_available"]:
        return {**fallback_model(prompt, context), "model": cfg}

    try:
        from openai import OpenAI
        client = OpenAI()
        msg = f"Contexto:\n{context[:3000]}\n\nPedido:\n{prompt}"
        res = client.chat.completions.create(
            model=cfg["model"],
            messages=[
                {"role": "system", "content": "Você é Eldora/NEURA. Responda com precisão, segurança e sem inventar fontes."},
                {"role": "user", "content": msg},
            ],
            max_tokens=cfg["max_tokens"],
            temperature=0.3,
        )
        return {
            "answer": res.choices[0].message.content,
            "llm_real_used": True,
            "model": cfg,
            "cost_controlled": True,
        }
    except Exception as e:
        return {
            **fallback_model(prompt, context),
            "model": cfg,
            "error": str(e)[:240],
        }
