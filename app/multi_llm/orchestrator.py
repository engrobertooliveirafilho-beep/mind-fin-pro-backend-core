from app.intent.intent_router import IntentRouter
from app.agents.agent_registry import AGENTS

class MultiLLMOrchestrator:

    def route(self,message):

        agent=IntentRouter().detect(message)

        provider=AGENTS.get(agent,"openai")

        return {
            "agent":agent,
            "provider":provider,
            "fallback":"groq",
            "status":"MULTI_LLM_RUNTIME_OPERATIONAL"
        }
