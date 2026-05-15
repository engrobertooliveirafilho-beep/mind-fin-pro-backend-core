from app.ingestion.file_downloader import FileDownloader
from app.ingestion.multimodal_router import MultiModalRouter
from app.vision.multi_vision_consensus_runtime import MultiVisionConsensusRuntime

class MediaHandler:

    def __init__(self):
        self.downloader = FileDownloader()
        self.router = MultiModalRouter()
        self.consensus = MultiVisionConsensusRuntime()

    def process(self, media_url, media_type, user_message="Analise profundamente esta mídia."):

        local_path = self.downloader.download(media_url, media_type)

        base_analysis = self.router.handle(
            media_type=media_type,
            media_url=media_url,
            local_path=local_path
        )

        if "image" in str(media_type).lower():
            return self.consensus.refine(
                question=user_message,
                base_analysis=base_analysis
            )

        return base_analysis
