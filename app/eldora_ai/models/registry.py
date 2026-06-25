class ModelRegistry:
    def __init__(self):
        self.models = {
            "sdxl": "stable-diffusion-xl",
            "animate_diff": "video-diffusion",
            "svd": "stable-video-diffusion",
            "whisper": "speech-to-text",
            "xtts": "text-to-speech"
        }

    def get(self, name):
        return self.models.get(name)
