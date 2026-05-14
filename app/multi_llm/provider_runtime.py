from app.multi_llm.providers.openai_provider import OpenAIProvider
from app.multi_llm.providers.groq_provider import GroqProvider

class ProviderRuntime:

    def __init__(self):

        self.providers = {
            "openai":OpenAIProvider(),
            "groq":GroqProvider()
        }

    def execute(self,provider,message):

        p=self.providers.get(provider)

        if not p:
            raise Exception(f"PROVIDER_NOT_FOUND:{provider}")

        if not p.health():
            raise Exception(f"PROVIDER_UNHEALTHY:{provider}")

        return p.chat(message)
