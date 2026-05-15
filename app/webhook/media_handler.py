from app.ingestion.file_downloader import FileDownloader
from app.ingestion.multimodal_router import MultiModalRouter

class MediaHandler:

    def __init__(self):
        self.downloader = FileDownloader()
        self.router = MultiModalRouter()

    def process(self, media_url, media_type):

        local_path = self.downloader.download(media_url, media_type)

        result = self.router.handle(
            media_type=media_type,
            media_url=media_url,
            local_path=local_path
        )

        return result
