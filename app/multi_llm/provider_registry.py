PROVIDERS = {
    "openai":{"type":"reasoning","latency":"medium","cost":"high","fallback":1},
    "anthropic":{"type":"reasoning","latency":"medium","cost":"high","fallback":2},
    "groq":{"type":"fast","latency":"ultra_low","cost":"low","fallback":3},
    "deepseek":{"type":"reasoning","latency":"low","cost":"low","fallback":4},
    "together":{"type":"general","latency":"medium","cost":"low","fallback":5},
    "cohere":{"type":"embedding","latency":"medium","cost":"medium","fallback":6},
    "mistral":{"type":"general","latency":"medium","cost":"low","fallback":7},
    "sambanova":{"type":"fast","latency":"ultra_low","cost":"medium","fallback":8},
    "huggingface":{"type":"multimodal","latency":"medium","cost":"low","fallback":9},
    "replicate":{"type":"vision","latency":"high","cost":"medium","fallback":10},
    "elevenlabs":{"type":"tts","latency":"low","cost":"medium","fallback":11},
    "speechmatics":{"type":"stt","latency":"medium","cost":"medium","fallback":12},
    "google_cloud":{"type":"infra","latency":"low","cost":"medium","fallback":13}
}
