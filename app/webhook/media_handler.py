from app.ingestion.file_downloader import FileDownloader
from app.ingestion.multimodal_router import MultiModalRouter

class MediaHandler:

    def __init__(self):
        self.downloader = FileDownloader()
        self.router = MultiModalRouter()

    def acknowledge(self, media_type):
        if "image" in str(media_type).lower():
            return "Imagem recebida. Envie ANALISAR IMAGEM para eu fazer a análise visual detalhada."
        return "Arquivo recebido. Envie ANALISAR ARQUIVO para eu interpretar o documento."

    def process(self, media_url, media_type, user_message="Analise esta mídia."):
        try:
            local_path = self.downloader.download(media_url, media_type)
            return self.router.handle(
                media_type=media_type,
                media_url=media_url,
                local_path=local_path,
                user_message=user_message
            )
        except Exception as e:
            return f"Falhei ao analisar a mídia: {type(e).__name__}: {str(e)[:120]}"
