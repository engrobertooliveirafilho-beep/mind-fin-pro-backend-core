from app.maf.gpu.engine import GPUInferenceEngine
from app.maf.image.sdxl_engine import SDXLImageEngine
from app.maf.video.video_engine import VideoEngine
from app.maf.audio.tts_engine import TTSEngine
from app.maf.orchestrator.router import MediaRouter
from app.maf.queue.queue import JobQueue
from app.maf.models.registry import ModelRegistry
from app.maf.storage.store import AssetStore

class MultimodalAIFactory:
    def __init__(self):
        self.gpu = GPUInferenceEngine()
        self.image = SDXLImageEngine()
        self.video = VideoEngine()
        self.audio = TTSEngine()
        self.router = MediaRouter()
        self.queue = JobQueue()
        self.models = ModelRegistry()
        self.storage = AssetStore()

    def generate(self, task_type, input_data):
        route = self.router.route(task_type, input_data)

        if task_type == "image":
            result = self.image.generate(input_data)

        elif task_type == "video":
            result = self.video.generate(input_data)

        elif task_type == "audio":
            result = self.audio.synthesize(input_data)

        else:
            result = {"error": "unsupported"}

        self.storage.save(task_type, result)

        return result
