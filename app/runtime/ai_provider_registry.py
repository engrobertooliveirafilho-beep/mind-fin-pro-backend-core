import os

PROVIDERS = [
    {"name":"openai","env":"OPENAI_API_KEY","model_env":"OPENAI_MODEL","default_model":"gpt-4o-mini","role":"general_factual"},
    {"name":"google_cloud","env":"GOOGLE_API_KEY","model_env":"GOOGLE_MODEL","default_model":"gemini-1.5-flash","role":"general_factual"},
    {"name":"groq","env":"GROQ_API_KEY","model_env":"GROQ_MODEL","default_model":"llama-3.1-70b-versatile","role":"fast_reasoning"},
    {"name":"anthropic","env":"ANTHROPIC_API_KEY","model_env":"ANTHROPIC_MODEL","default_model":"claude-3-5-sonnet-latest","role":"deep_reasoning"},
    {"name":"cohere","env":"COHERE_API_KEY","model_env":"COHERE_MODEL","default_model":"command-r-plus","role":"rag_text"},
    {"name":"mistral","env":"MISTRAL_API_KEY","model_env":"MISTRAL_MODEL","default_model":"mistral-large-latest","role":"european_reasoning"},
    {"name":"together","env":"TOGETHER_API_KEY","model_env":"TOGETHER_MODEL","default_model":"meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo","role":"open_model"},
    {"name":"deepseek","env":"DEEPSEEK_API_KEY","model_env":"DEEPSEEK_MODEL","default_model":"deepseek-chat","role":"cheap_reasoning"},
    {"name":"perplexity","env":"PERPLEXITY_API_KEY","model_env":"PERPLEXITY_MODEL","default_model":"sonar","role":"web_factual"},
    {"name":"sambanova","env":"SAMBANOVA_API_KEY","model_env":"SAMBANOVA_MODEL","default_model":"Meta-Llama-3.1-70B-Instruct","role":"fast_open_model"},
    {"name":"elevenlabs","env":"ELEVENLABS_API_KEY","model_env":"ELEVENLABS_MODEL","default_model":"tts","role":"voice"},
    {"name":"replicate","env":"REPLICATE_API_TOKEN","model_env":"REPLICATE_MODEL","default_model":"generic","role":"image_video_model"},
    {"name":"huggingface","env":"HUGGINGFACE_API_KEY","model_env":"HUGGINGFACE_MODEL","default_model":"generic","role":"open_models"},
    {"name":"speechmatics","env":"SPEECHMATICS_API_KEY","model_env":"SPEECHMATICS_MODEL","default_model":"asr","role":"speech_to_text"},
]

FALLBACK_ORDER = [
    "openai","groq","anthropic","mistral","deepseek","perplexity",
    "google_cloud","cohere","together","sambanova","huggingface"
]

def provider_registry_status():
    out = []
    for p in PROVIDERS:
        configured = bool(os.getenv(p["env"], "").strip())
        out.append({
            "name": p["name"],
            "env": p["env"],
            "configured": configured,
            "model": os.getenv(p["model_env"], p["default_model"]),
            "role": p["role"],
        })
    return {
        "total": len(PROVIDERS),
        "configured_count": sum(1 for x in out if x["configured"]),
        "missing_count": sum(1 for x in out if not x["configured"]),
        "fallback_order": FALLBACK_ORDER,
        "providers": out,
    }

def configured_text_providers():
    status = provider_registry_status()["providers"]
    names = {p["name"]: p for p in status if p["configured"]}
    return [names[n] for n in FALLBACK_ORDER if n in names]
