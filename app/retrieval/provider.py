
class RetrievalProvider:
    def retrieve(self, message, history):
        text = "\n".join([(h.get("message") or h.get("content") or "") for h in history])
        low=text.lower()
        facts={}
        if "roberto" in low: facts["nome"]="Roberto"
        if "matemática" in low or "matematica" in low: facts["estudo"]="matemática"
        if "sexta" in low: facts["prova"]="sexta"
        return {"facts":facts,"history_text":text,"history_count":len(history)}
