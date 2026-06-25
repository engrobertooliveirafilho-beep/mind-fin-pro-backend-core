class ModelRegistry:
    def __init__(self):
        self.models = {
            "sdxl": "v1",
            "svd": "v1",
            "tts": "v1"
        }

    def get(self, name):
        return self.models.get(name, "not_found")
