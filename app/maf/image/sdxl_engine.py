class SDXLImageEngine:
    def generate(self, prompt):
        return {
            "model": "SDXL",
            "image": f"generated_image_from_{prompt}"
        }
