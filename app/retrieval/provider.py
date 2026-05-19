class RetrievalProvider:
    def search(self, query: str = "", context: dict | None = None) -> dict:
        text = (query or "").lower()
        facts = {}

        if "roberto" in text:
            facts["name"] = "Roberto"

        if "ram 2500" in text or "ram 3500" in text:
            facts["topic"] = "comparativo RAM 2500 vs RAM 3500"

        elif "diesel" in text:
            facts["topic"] = "motor diesel"

        elif "carro" in text or "carros" in text:
            facts["topic"] = "carros"

        elif "implant" in text or "eldora" in text or "humaniza" in text:
            facts["topic"] = "implantações Eldora"

        elif "math" in text:
            facts["topic"] = "tema técnico"

        return {
            "query": query,
            "facts": facts,
            "context": context or {},
            "source": "retrieval_provider_safe_v2"
        }
