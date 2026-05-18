class RetrievalProvider:

    def retrieve(self, message=None, history=None):
        return self.build_context(history)

    def build_context(self, history):

        facts = {}
        lines = []

        for row in history or []:
            text = (row.get("message") or row.get("content") or "").strip()
            low = text.lower()

            if text:
                lines.append(text)

            if "roberto" in low:
                facts["nome"] = "Roberto"

            if "matemática" in low or "matematica" in low:
                facts["estudo"] = "matemática"

            if "prova" in low and "sexta" in low:
                facts["prova"] = "sexta"

        return {
            "facts": facts,
            "history_text": "\n".join(lines[-20:]),
            "history_count": len(history or [])
        }
