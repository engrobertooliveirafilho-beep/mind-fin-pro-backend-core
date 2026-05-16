class MediaHandler:

    def __init__(self):
        pass

    def process(self, media_url, media_type, user_message="Analise esta mídia."):

        if "image" in str(media_type).lower():
            return "Imagem recebida. Para análise profunda, envie: ANALISAR IMAGEM. Vou usar o contexto visual como base."

        return "Arquivo recebido. Para análise do documento, envie: ANALISAR ARQUIVO."
