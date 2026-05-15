from app.ingestion.file_downloader import FileDownloader
from app.ingestion.multimodal_router import MultiModalRouter
from app.vision.multi_vision_consensus_runtime import MultiVisionConsensusRuntime

class MediaHandler:

    def __init__(self):
        self.downloader = FileDownloader()
        self.router = MultiModalRouter()
        self.consensus = MultiVisionConsensusRuntime()

    def process(self, media_url, media_type, user_message="Analise esta mídia."):

        try:
            local_path = self.downloader.download(media_url, media_type)
        except Exception as e:
            return f"Recebi a mídia, mas não consegui baixar o arquivo da Twilio: {str(e)[:160]}"

        try:
            base_analysis = self.router.handle(
                media_type=media_type,
                media_url=media_url,
                local_path=local_path
            )
        except Exception as e:
            return f"Recebi a mídia, mas falhei na análise visual inicial: {str(e)[:160]}"

        if "image" not in str(media_type).lower():
            return base_analysis

        try:
            refined = self.consensus.refine(
                question=user_message,
                base_analysis=base_analysis
            )

            if refined and len(str(refined).strip()) > 20:
                return refined

        except Exception:
            pass

        return base_analysis
