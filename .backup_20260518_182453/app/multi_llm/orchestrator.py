from app.intent.intent_router import IntentRouter
from app.agents.agent_registry import AGENTS
from app.multi_llm.provider_runtime import ProviderRuntime

class MultiLLMOrchestrator:

    def route(self,message):

        agent=IntentRouter().detect(message)

        provider=AGENTS.get(agent,"openai")

        runtime=ProviderRuntime()

        try:
            result=runtime.execute(provider,message)
            status="PRIMARY_OK"

        except Exception as e:

            result=runtime.execute("groq",message)

            status=f"FALLBACK_OK:{str(e)}"

        return {
            "agent":agent,
            "provider":provider,
            "fallback":"groq",
            "runtime_status":status,
            "result":result
        }
