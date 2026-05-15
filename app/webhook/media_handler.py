from app.ingestion.file_downloader import FileDownloader
from app.ingestion.multimodal_router import MultiModalRouter

class MediaHandler:

    def __init__(self):
        self.downloader = FileDownloader()
        self.router = MultiModalRouter()

    def process(self, media_url, media_type, user_message="Analise esta mídia."):

        try:
            print("MEDIA_HANDLER_START")
            local_path = self.downloader.download(media_url, media_type)
            print(f"MEDIA_DOWNLOADED={local_path}")

            result = self.router.handle(
                media_type=media_type,
                media_url=media_url,
                local_path=local_path,
                user_message=user_message
            )

            print("MEDIA_HANDLER_DONE")
            return result

        except Exception as e:
            print(f"MEDIA_HANDLER_ERROR={type(e).__name__}: {str(e)[:200]}")
            return f"Recebi a mídia, mas falhei ao analisar: {type(e).__name__}: {str(e)[:120]}"
