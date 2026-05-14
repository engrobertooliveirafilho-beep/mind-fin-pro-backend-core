from app.multi_llm.providers.base_provider import GenericHTTPProvider

def anthropic():

    def extract(data):

        try:

            if "content" in data and len(data["content"]) > 0:

                block=data["content"][0]

                if isinstance(block,dict):

                    if "text" in block:
                        return block["text"]

                    if "content" in block:
                        return str(block["content"])

                return str(block)

            if "error" in data:
                return f"ANTHROPIC_API_ERROR: {data['error']}"

            return str(data)

        except Exception as e:
            return f"ANTHROPIC_PARSE_ERROR: {str(e)}"

    return GenericHTTPProvider(
        "anthropic",
        "ANTHROPIC",
        "https://api.anthropic.com/v1/messages",
        lambda k: {
            "x-api-key":k,
            "anthropic-version":"2023-06-01",
            "content-type":"application/json"
        },
        lambda m: {
            "model":"claude-3-5-haiku-latest",
            "max_tokens":700,
            "messages":[
                {
                    "role":"user",
                    "content":m
                }
            ]
        },
        extract
    )

def deepseek():
    return GenericHTTPProvider("deepseek","DEEPSEEK","https://api.deepseek.com/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"deepseek-chat","messages":[{"role":"user","content":m}],"temperature":0.3},
        lambda d: d["choices"][0]["message"]["content"])

def perplexity():
    return GenericHTTPProvider("perplexity","PERPLEXITY","https://api.perplexity.ai/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"sonar","messages":[{"role":"user","content":m}]},
        lambda d: d["choices"][0]["message"]["content"])

def mistral():
    return GenericHTTPProvider("mistral","MISTRAL","https://api.mistral.ai/v1/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"mistral-small-latest","messages":[{"role":"user","content":m}]},
        lambda d: d["choices"][0]["message"]["content"])

def together():
    return GenericHTTPProvider("together","TOGETHER","https://api.together.xyz/v1/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"meta-llama/Llama-3.3-70B-Instruct-Turbo","messages":[{"role":"user","content":m}]},
        lambda d: d["choices"][0]["message"]["content"])

def sambanova():
    return GenericHTTPProvider("sambanova","SAMBANOVA","https://api.sambanova.ai/v1/chat/completions",
        lambda k: {"Authorization":f"Bearer {k}","Content-Type":"application/json"},
        lambda m: {"model":"Meta-Llama-3.1-8B-Instruct","messages":[{"role":"user","content":m}]},
        lambda d: d["choices"][0]["message"]["content"])

def huggingface():
    return GenericHTTPProvider("huggingface","HUGGING")

def replicate():
    return GenericHTTPProvider("replicate","REPLICATE")

def elevenlabs():
    return GenericHTTPProvider("elevenlabs","ELEVENLABS")

def speechmatics():
    return GenericHTTPProvider("speechmatics","SPEECHMATICS")

def cohere():
    return GenericHTTPProvider("cohere","COHERE")

