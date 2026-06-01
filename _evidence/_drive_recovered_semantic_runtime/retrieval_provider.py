
class RetrievalProvider:
    def retrieve_context(self, query: str, intent: str):
        return [
            {
                "source": "CORE_TRUE_semantic_capability_layer",
                "content": f"Contexto recuperado para intent={intent}: {query[:120]}",
                "confidence": 0.82
            }
        ]

    def retrieve_agents(self, intent: str):
        return {"agent_id": f"{intent}_agent", "confidence": 0.9}

    def retrieve_prompts(self, intent: str):
        return {"template": f"Responda como NEURA para intent={intent}, com clareza e ação prática."}
