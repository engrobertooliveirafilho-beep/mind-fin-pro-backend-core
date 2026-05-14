from app.multi_llm.providers.openai_provider import OpenAIProvider
from app.multi_llm.providers.groq_provider import GroqProvider
from app.multi_llm.providers.extended_providers import anthropic, deepseek, perplexity, mistral, together, sambanova, huggingface, replicate, elevenlabs, speechmatics, cohere

class ProviderRuntime:
    def __init__(self):
        self.providers={
            "openai":OpenAIProvider(),
            "groq":GroqProvider(),
            "anthropic":anthropic(),
            "deepseek":deepseek(),
            "perplexity":perplexity(),
            "mistral":mistral(),
            "together":together(),
            "sambanova":sambanova(),
            "huggingface":huggingface(),
            "replicate":replicate(),
            "elevenlabs":elevenlabs(),
            "speechmatics":speechmatics(),
            "cohere":cohere()
        }

    def health_report(self):
        return {k:v.health() for k,v in self.providers.items()}

    def execute(self,provider,message):
        p=self.providers.get(provider)
        if not p:
            raise Exception(f"PROVIDER_NOT_FOUND:{provider}")
        if not p.health():
            raise Exception(f"PROVIDER_UNHEALTHY:{provider}")
        return p.chat(message)
