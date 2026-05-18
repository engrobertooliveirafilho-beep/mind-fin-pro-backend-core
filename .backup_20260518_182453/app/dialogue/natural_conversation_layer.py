class NaturalConversationLayer:
    def shape(self, response: str, intent: str):
        return (response or 'Entendi. Me mande sua dÃºvida ou material de estudo.').strip()