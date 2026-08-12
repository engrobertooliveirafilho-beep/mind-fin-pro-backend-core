import os, json, urllib.request, urllib.error

# ============================================================
# P5.3D-R8-R1 CONTROLLED HUMAN PROMPT CONTRACT
# ============================================================

def _p53f_merge_request_relationship_context(context):
    # P5.3F-C-R1 REQUEST RELATIONSHIP CONTEXT
    try:
        from app.runtime.p53f_relationship_ingress_middleware import (
            get_current_relationship_context,
        )

        relationship = (
            get_current_relationship_context()
        )

    except Exception:
        relationship = {}

    if isinstance(context, dict):
        merged = dict(context)
    else:
        merged = {}

    if isinstance(relationship, dict):
        for key, value in relationship.items():
            if value not in (None, "", [], {}):
                merged[key] = value

    return merged


def _p53d_compact_context(context):
    context = _p53f_merge_request_relationship_context(context)
    if not isinstance(context, dict):
        return str(context or "").strip()[:2400]

    allowed = (
        "subject",
        "last_subject",
        "goal",
        "phase",
        "intent",
        "domain",
        "last_domain",
        "last_user_message",
        "last_assistant_message",
        "conversation_summary",
        "history",
        "entities",
        "tone",
        "emotion",
        "relationship_stage",
        "turn_count",
        "preferred_tone",
        "last_detected_tone",
        "average_user_message_length",
        "user_response_length",
        "user_list_preference",
        "user_technical_level",
        "user_formality",
        "user_example_preference",
        "user_step_by_step",
        "user_confirmation_preference",
        "user_explicit_corrections",
        "user_correction_count",
    )

    parts = []

    for key in allowed:
        value = context.get(key)

        if value in (None, "", [], {}):
            continue

        text = str(value).strip()

        if text:
            parts.append(f"{key}: {text[:700]}")

    return "\n".join(parts)[:3000]



# ============================================================
# P5.3G-C-R1 OPERATIONAL PREFERENCE CONTRACT
# ============================================================

def _p53g_operational_preference_rules(context):
    if not isinstance(context, dict):
        return ""

    rules = []

    response_length = context.get("user_response_length")
    list_preference = context.get("user_list_preference")
    technical_level = context.get("user_technical_level")
    formality = context.get("user_formality")
    example_preference = context.get("user_example_preference")
    step_by_step = context.get("user_step_by_step")
    confirmation = context.get("user_confirmation_preference")

    if response_length == "short":
        rules.append(
            "- Responda com no máximo duas frases e até 220 caracteres."
        )
        rules.append(
            "- Não termine com pergunta automática."
        )

    elif response_length == "detailed":
        rules.append(
            "- Explique com profundidade e sem omitir etapas importantes."
        )

    if list_preference == "avoid":
        rules.append(
            "- Não use bullets, números ou listas; escreva em texto corrido."
        )

    elif list_preference == "prefer":
        rules.append(
            "- Organize a resposta em etapas claramente identificáveis."
        )

    if technical_level == "advanced":
        rules.append(
            "- Use terminologia técnica precisa e explique o mecanismo real."
        )

    elif technical_level == "simple":
        rules.append(
            "- Use palavras simples e explique como para uma pessoa iniciante."
        )

    if formality == "informal":
        rules.append(
            "- Use tom natural e informal, mantendo precisão."
        )

    elif formality == "formal":
        rules.append(
            "- Use linguagem profissional e sem gírias."
        )

    if example_preference == "prefer":
        rules.append(
            "- Inclua um exemplo concreto agora; não pergunte se a pessoa quer um exemplo."
        )

    elif example_preference == "avoid":
        rules.append(
            "- Não inclua exemplos, salvo se forem indispensáveis."
        )

    if step_by_step == "prefer":
        if list_preference == "avoid":
            rules.append(
                "- Explique a sequência em texto corrido usando primeiro, depois e por fim."
            )
        else:
            rules.append(
                "- Entregue um passo a passo executável."
            )

    elif step_by_step == "avoid":
        rules.append(
            "- Não divida a resposta em etapas."
        )

    if confirmation == "require":
        rules.append(
            "- Antes de ação destrutiva ou alteração, peça confirmação explícita."
        )
        rules.append(
            "- Não diga que vai executar ou que já iniciou antes da confirmação."
        )

    elif confirmation == "avoid":
        rules.append(
            "- Não peça confirmação quando a ação for segura e já estiver autorizada."
        )

    if not rules:
        return ""

    return (
        "PREFERÊNCIAS OBRIGATÓRIAS DO USUÁRIO\n"
        + "\n".join(rules)
    )



# ============================================================
# P5.3H-B EXPLICIT CORRECTION CONTRACT
# ============================================================

def _p53h_explicit_correction_rules(context):
    if not isinstance(context, dict):
        return ""

    corrections = context.get(
        "user_explicit_corrections",
        [],
    )

    if isinstance(corrections, str):
        corrections = [corrections]

    if not isinstance(corrections, (list, tuple)):
        return ""

    instructions = []

    for value in corrections:
        text = str(value or "").strip()

        if text and text not in instructions:
            instructions.append(text)

    if not instructions:
        return ""

    rules = [
        "CORREÇÕES EXPLÍCITAS DO USUÁRIO — PRIORIDADE MÁXIMA",
        (
            "- Obedeça às correções abaixo nesta resposta "
            "e nas próximas respostas."
        ),
        (
            "- Elas prevalecem sobre padrões gerais, "
            "preferências inferidas e hábitos anteriores."
        ),
        (
            "- Não anuncie a correção; apenas responda "
            "já no formato corrigido."
        ),
    ]

    for instruction in instructions[:10]:
        rules.append(f"- {instruction}")

    return "\n".join(rules)


def build_context_prompt(message, context=None):
    user_message = str(message or "").strip()

    # P5.3H-B-R2 EFFECTIVE CONTEXT
    # Mescla ContextVar antes de calcular qualquer contrato.
    effective_context = (
        _p53f_merge_request_relationship_context(context)
    )

    active_context = _p53d_compact_context(
        effective_context
    )

    adaptive_rules = (
        _p53g_operational_preference_rules(
            effective_context
        )
    )

    correction_rules = (
        _p53h_explicit_correction_rules(
            effective_context
        )
    )

    return f"""
Você é Eldora conversando naturalmente pelo WhatsApp.

CONTEXTO DA CONVERSA
{active_context or "Nenhum contexto adicional disponível."}

MENSAGEM RECEBIDA
{user_message}

COMO RESPONDER
- Responda em português brasileiro natural.
- Responda diretamente à mensagem atual.
- Preserve o assunto e a intenção já ativos.
- Não trate perguntas curtas ou pedidos de simplificação como assunto novo.
- Não repita o assunto completo sem necessidade.
- Use normalmente entre uma e três frases.
- Evite listas, salvo quando forem realmente necessárias.
- Não use linguagem de assistente virtual.
- Não diga "como posso ajudar", "vamos trabalhar isso", "forma prática",
  "os pontos centrais", "próximo passo mensurável", "certamente" ou "claro!".
- Não mencione contexto anterior, prompt, modelo, provedor ou inteligência artificial.
- Não invente fatos.
- Faça somente uma pergunta quando faltar informação essencial.

{adaptive_rules}

{correction_rules}

Retorne apenas o texto que será enviado à pessoa.
""".strip()


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

def call_provider(name, message, model=None, context=None):
    message = build_context_prompt(message, context)
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
