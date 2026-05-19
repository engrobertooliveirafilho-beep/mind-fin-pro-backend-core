class AdaptiveSocialDialogue:
    def adapt(self, text: str, message: str) -> str:
        m = (message or "").lower()
        if "marca" in m or "produto" in m or "neura" in m:
            return text + " Como produto, a prioridade é consistência: mesmo rosto, mesma energia e evolução visual controlada."
        if "estudante" in m:
            return text + " Para estudante, ela deve parecer didática, paciente e acessível."
        if "marketing" in m or "branding" in m:
            return text + " Em marketing, isso vira ativo de retenção: rosto reconhecível, tom constante e presença repetida no WhatsApp/status."
        return text
