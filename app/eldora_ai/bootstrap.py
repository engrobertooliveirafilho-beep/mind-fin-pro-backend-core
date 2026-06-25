from app.eldora_ai.image.sdxl import SDXL
from app.eldora_ai.video.engine import VideoGenerator
from app.eldora_ai.audio.engine import AudioEngine
from app.eldora_ai.media_pipeline.ffmpeg import FFmpegPipeline
from app.eldora_ai.models.registry import ModelRegistry

class EldoraAIFactory:
    def __init__(self):
        self.models = ModelRegistry()
        self.image = SDXL()
        self.video = VideoGenerator()
        self.audio = AudioEngine()
        self.media = FFmpegPipeline()

    def generate(self, task_type, prompt):
        if task_type == "image":
            return self.image.generate(prompt)

        if task_type == "video":
            return self.video.generate(prompt)

        if task_type == "audio":
            return self.audio.synthesize(prompt)

        return {"error": "unsupported task"}
