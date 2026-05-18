from fastapi import APIRouter
import os

router=APIRouter()

@router.get("/admin/runtime/env-audit")
def env_audit():

    keys = [
        "OPENAI_API_KEY",
        "GROQ_API_KEY",
        "ANTHROPIC_API_KEY",
        "DEEPSEEK_API_KEY",
        "PERPLEXITY_API_KEY",
        "COHERE_API_KEY",
        "MISTRAL_API_KEY",
        "TOGETHER_API_KEY",
        "SAMBANOVA_API_KEY",
        "HUGGINGFACE_API_KEY",
        "REPLICATE_API_TOKEN",
        "ELEVENLABS_API_KEY",
        "SPEECHMATICS_API_KEY"
    ]

    return {
        "status":"ENV_AUDIT",
        "envs": {
            k: bool(os.getenv(k,""))
            for k in keys
        }
    }
