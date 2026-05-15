from app.ingestion.file_downloader import FileDownloader
from app.ingestion.multimodal_router import MultiModalRouter

class MediaHandler:

    def __init__(self):
        self.downloader = FileDownloader()
        self.router = MultiModalRouter()

    def process(self, media_url, media_type, user_message="Analise esta mídia."):

        try:
            local_path = self.downloader.download(media_url, media_type)

            return self.router.handle(
                media_type=media_type,
                media_url=media_url,
                local_path=local_path
            )

        except Exception as e:
            return f"Recebi a mídia, mas não consegui processar agora: {type(e).__name__}: {str(e)[:120]}"
