import os, json, urllib.request, urllib.error

def _post_json(url, headers, payload, timeout=35):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type":"application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, json.loads(r.read().decode("utf-8")), None
    except Exception as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="ignore")[:500] if hasattr(e, "read") else ""
        except Exception:
            pass
        return False, None, f"{type(e).__name__}:{getattr(e,'code','')}:{body}"

def _chat_payload(message, model):
    return {
        "model": model,
        "messages": [
            {"role":"system","content":"Responda em PT-BR, WhatsApp, curto, útil, factual e sem inventar."},
            {"role":"user","content":message},
        ],
        "temperature":0.2,
        "max_tokens":350,
    }

def call_provider(name, message, model=None):
    if name == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        r = client.chat.completions.create(
            model=model or os.getenv("OPENAI_MODEL","gpt-4o-mini"),
            messages=[{"role":"user","content":message}],
            temperature=0.2,
            max_tokens=350,
        )
        return r.choices[0].message.content.strip()

    if name == "groq":
        ok,d,e=_post_json("https://api.groq.com/openai/v1/chat/completions",{"Authorization":"Bearer "+os.getenv("GROQ_API_KEY","")},_chat_payload(message, model or os.getenv("GROQ_MODEL","llama-3.1-70b-versatile")))
        if not ok: raise RuntimeError(e)
        return d["choices"][0]["message"]["content"].strip()

    if name == "deepseek":
        ok,d,e=_post_json("https://api.deepseek.com/chat/completions",{"Authorization":"Bearer "+os.getenv("DEEPSEEK_API_KEY","")},_chat_payload(message, model or os.getenv("DEEPSEEK_MODEL","deepseek-chat")))
        if not ok: raise RuntimeError(e)
        return d["choices"][0]["message"]["content"].strip()

    if name == "perplexity":
        ok,d,e=_post_json("https://api.perplexity.ai/chat/completions",{"Authorization":"Bearer "+os.getenv("PERPLEXITY_API_KEY","")},_chat_payload(message, model or os.getenv("PERPLEXITY_MODEL","sonar")))
        if not ok: raise RuntimeError(e)
        return d["choices"][0]["message"]["content"].strip()

    if name == "together":
        ok,d,e=_post_json("https://api.together.xyz/v1/chat/completions",{"Authorization":"Bearer "+os.getenv("TOGETHER_API_KEY","")},_chat_payload(message, model or os.getenv("TOGETHER_MODEL","meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo")))
        if not ok: raise RuntimeError(e)
        return d["choices"][0]["message"]["content"].strip()

    if name == "sambanova":
        ok,d,e=_post_json("https://api.sambanova.ai/v1/chat/completions",{"Authorization":"Bearer "+os.getenv("SAMBANOVA_API_KEY","")},_chat_payload(message, model or os.getenv("SAMBANOVA_MODEL","Meta-Llama-3.1-70B-Instruct")))
        if not ok: raise RuntimeError(e)
        return d["choices"][0]["message"]["content"].strip()

    if name == "anthropic":
        payload={"model":model or os.getenv("ANTHROPIC_MODEL","claude-3-5-sonnet-latest"),"max_tokens":350,"temperature":0.2,"messages":[{"role":"user","content":message}]}
        ok,d,e=_post_json("https://api.anthropic.com/v1/messages",{"x-api-key":os.getenv("ANTHROPIC_API_KEY",""),"anthropic-version":"2023-06-01"},payload)
        if not ok: raise RuntimeError(e)
        return "".join([x.get("text","") for x in d.get("content",[])]).strip()

    if name == "mistral":
        ok,d,e=_post_json("https://api.mistral.ai/v1/chat/completions",{"Authorization":"Bearer "+os.getenv("MISTRAL_API_KEY","")},_chat_payload(message, model or os.getenv("MISTRAL_MODEL","mistral-large-latest")))
        if not ok: raise RuntimeError(e)
        return d["choices"][0]["message"]["content"].strip()

    if name == "cohere":
        payload={"model":model or os.getenv("COHERE_MODEL","command-r-plus"),"message":message,"temperature":0.2}
        ok,d,e=_post_json("https://api.cohere.ai/v1/chat",{"Authorization":"Bearer "+os.getenv("COHERE_API_KEY","")},payload)
        if not ok: raise RuntimeError(e)
        return d.get("text","").strip()

    if name == "google_cloud":
        key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_CLOUD_API_KEY")
        m=model or os.getenv("GOOGLE_MODEL","gemini-1.5-flash")
        payload={"contents":[{"parts":[{"text":message}]}],"generationConfig":{"temperature":0.2,"maxOutputTokens":350}}
        ok,d,e=_post_json(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}",{},payload)
        if not ok: raise RuntimeError(e)
        return d["candidates"][0]["content"]["parts"][0]["text"].strip()

    if name == "huggingface":
        raise RuntimeError("huggingface_text_adapter_requires_model_endpoint")

    raise RuntimeError("adapter_not_implemented")
