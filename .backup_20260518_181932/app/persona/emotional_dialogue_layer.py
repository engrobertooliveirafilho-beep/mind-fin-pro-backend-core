class EmotionalDialogueLayer:
    def polish(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return "Posso te ajudar a ajustar isso com mais clareza."
        return text + " Minha recomendação: mexer pouco, testar com usuários reais e proteger a identidade visual principal."
