import os

PROVIDERS = [
    {"name":"openai","envs":["OPENAI_API_KEY","OPENAI_KEY"],"model_env":"OPENAI_MODEL","default_model":"gpt-4o-mini","role":"general_factual"},
    {"name":"google_cloud","envs":["GOOGLE_API_KEY","GEMINI_API_KEY","GOOGLE_CLOUD_API_KEY"],"model_env":"GOOGLE_MODEL","default_model":"gemini-1.5-flash","role":"general_factual"},
    {"name":"groq","envs":["GROQ_API_KEY","GROQCLOUD_API_KEY","GROQ_KEY"],"model_env":"GROQ_MODEL","default_model":"llama-3.1-70b-versatile","role":"fast_reasoning"},
    {"name":"anthropic","envs":["ANTHROPIC_API_KEY","CLAUDE_API_KEY"],"model_env":"ANTHROPIC_MODEL","default_model":"claude-3-5-sonnet-latest","role":"deep_reasoning"},
    {"name":"cohere","envs":["COHERE_API_KEY","COHERE_KEY"],"model_env":"COHERE_MODEL","default_model":"command-r-plus","role":"rag_text"},
    {"name":"mistral","envs":["MISTRAL_API_KEY","MISTRAL_KEY"],"model_env":"MISTRAL_MODEL","default_model":"mistral-large-latest","role":"european_reasoning"},
    {"name":"together","envs":["TOGETHER_API_KEY","TOGETHERAI_API_KEY","TOGETHER_KEY"],"model_env":"TOGETHER_MODEL","default_model":"meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo","role":"open_model"},
    {"name":"deepseek","envs":["DEEPSEEK_API_KEY","DEEPSEEK_KEY"],"model_env":"DEEPSEEK_MODEL","default_model":"deepseek-chat","role":"cheap_reasoning"},
    {"name":"perplexity","envs":["PERPLEXITY_API_KEY","PERPLEXITY_KEY","PPLX_API_KEY"],"model_env":"PERPLEXITY_MODEL","default_model":"sonar","role":"web_factual"},
    {"name":"sambanova","envs":["SAMBANOVA_API_KEY","SAMBANOVA_KEY"],"model_env":"SAMBANOVA_MODEL","default_model":"Meta-Llama-3.1-70B-Instruct","role":"fast_open_model"},
    {"name":"elevenlabs","envs":["ELEVENLABS_API_KEY","ELEVENLABS_KEY"],"model_env":"ELEVENLABS_MODEL","default_model":"tts","role":"voice"},
    {"name":"replicate","envs":["REPLICATE_API_TOKEN","REPLICATE_API_KEY"],"model_env":"REPLICATE_MODEL","default_model":"generic","role":"image_video_model"},
    {"name":"huggingface","envs":["HUGGINGFACE_API_KEY","HF_TOKEN","HUGGINGFACEHUB_API_TOKEN"],"model_env":"HUGGINGFACE_MODEL","default_model":"generic","role":"open_models"},
    {"name":"speechmatics","envs":["SPEECHMATICS_API_KEY","SPEECHMATICS_KEY"],"model_env":"SPEECHMATICS_MODEL","default_model":"asr","role":"speech_to_text"},
]

FALLBACK_ORDER = ["openai","mistral","deepseek","perplexity","google_cloud","cohere","together","sambanova","huggingface","groq","anthropic"]

def _active_env(envs):
    for e in envs:
        if os.getenv(e, "").strip():
            return e
    return None

def provider_registry_status():
    out=[]
    for p in PROVIDERS:
        active=_active_env(p["envs"])
        out.append({
            "name":p["name"],
            "envs":p["envs"],
            "active_env":active,
            "configured":bool(active),
            "model":os.getenv(p["model_env"],p["default_model"]),
            "role":p["role"],
        })
    return {
        "total":len(PROVIDERS),
        "configured_count":sum(1 for x in out if x["configured"]),
        "missing_count":sum(1 for x in out if not x["configured"]),
        "fallback_order":FALLBACK_ORDER,
        "providers":out,
    }

def configured_text_providers():
    status=provider_registry_status()["providers"]
    names={p["name"]:p for p in status if p["configured"]}
    return [names[n] for n in FALLBACK_ORDER if n in names]

