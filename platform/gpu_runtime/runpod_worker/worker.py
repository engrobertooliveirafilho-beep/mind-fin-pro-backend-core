import torch
from diffusers import StableDiffusionXLPipeline

class GPUWorker:

    def __init__(self):
        self.pipe = None

    def load_sdxl(self):
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            'stabilityai/stable-diffusion-xl-base-1.0',
            torch_dtype=torch.float16
        ).to('cuda')

    def generate_image(self, prompt):
        return self.pipe(prompt).images[0]
