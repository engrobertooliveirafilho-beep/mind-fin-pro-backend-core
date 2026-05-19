class RetrievalProvider:
    def retrieve(self, message=None, history=None):
        query = message or ""
        ctx = self.build_context(history or [])
        direct = self.search(query, ctx)
        merged = dict(ctx)
        merged["facts"].update(direct.get("facts", {}))
        merged["query"] = query
        merged["source"] = "retrieval_provider_safe_v3"
        return merged

    def build_context(self, history=None):
        facts = {}
        lines = []

        for row in history or []:
            text = (row.get("message") or row.get("content") or "").strip()
            low = text.lower()

            if text:
                lines.append(text)

            if "roberto" in low:
                facts["name"] = "Roberto"

            if "ram 2500" in low or "ram 3500" in low:
                facts["topic"] = "comparativo RAM 2500 vs RAM 3500"
            elif "diesel" in low:
                facts["topic"] = "motor diesel"
            elif "carro" in low or "carros" in low:
                facts["topic"] = "carros"
            elif "implant" in low or "eldora" in low or "humaniza" in low:
                facts["topic"] = "implantações Eldora"

        return {
            "facts": facts,
            "history_text": "\n".join(lines[-20:]),
            "history_count": len(history or [])
        }

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
            "source": "retrieval_provider_safe_v3"
        }
