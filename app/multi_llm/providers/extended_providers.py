from app.multi_llm.providers.base_provider import GenericHTTPProvider

def anthropic():
    return GenericHTTPProvider(
        "anthropic","ANTHROPIC_API_KEY","https://api.anthropic.com/v1/messages",
        lambda k: {"x-api-key":k,"anthropic-version":"2023-06-01","content-type":"application/json"},
        lambda m: {"model":"claude-3-5-haiku-latest","max_tokens":700,"messages":[{"role":"user","content":m}]},
        lambda d: d["content"][0]["text"]
    )

def deepseek():
    return GenericHTTPProvider(
        "deepseek","DEEPSEEK_API_KEY","https://api.deepseek.com/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"deepseek-chat","messages":[{"role":"user","content":m}],"temperature":0.3},
        lambda d: d["choices"][0]["message"]["content"]
    )

def perplexity():
    return GenericHTTPProvider(
        "perplexity","PERPLEXITY_API_KEY","https://api.perplexity.ai/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"sonar","messages":[{"role":"user","content":m}]},
        lambda d: d["choices"][0]["message"]["content"]
    )

def mistral():
    return GenericHTTPProvider(
        "mistral","MISTRAL_API_KEY","https://api.mistral.ai/v1/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"mistral-small-latest","messages":[{"role":"user","content":m}]},
        lambda d: d["choices"][0]["message"]["content"]
    )

def together():
    return GenericHTTPProvider(
        "together","TOGETHER_API_KEY","https://api.together.xyz/v1/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"meta-llama/Llama-3.3-70B-Instruct-Turbo","messages":[{"role":"user","content":m}]},
        lambda d: d["choices"][0]["message"]["content"]
    )

def sambanova():
    return GenericHTTPProvider(
        "sambanova","SAMBANOVA_API_KEY","https://api.sambanova.ai/v1/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"Meta-Llama-3.1-8B-Instruct","messages":[{"role":"user","content":m}]},
        lambda d: d["choices"][0]["message"]["content"]
    )

def huggingface():
    return GenericHTTPProvider("huggingface","HUGGINGFACE_API_KEY")

def replicate():
    return GenericHTTPProvider("replicate","REPLICATE_API_TOKEN")

def elevenlabs():
    return GenericHTTPProvider("elevenlabs","ELEVENLABS_API_KEY")

def speechmatics():
    return GenericHTTPProvider("speechmatics","SPEECHMATICS_API_KEY")

def cohere():
    return GenericHTTPProvider("cohere","COHERE_API_KEY")
