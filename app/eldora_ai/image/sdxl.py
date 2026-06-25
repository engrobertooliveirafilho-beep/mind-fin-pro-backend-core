class SDXL:
    def generate(self, prompt):
        return {
            "type": "image",
            "model": "SDXL",
            "output": f"image_from_{prompt}"
        }
