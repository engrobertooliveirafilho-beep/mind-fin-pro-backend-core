MODEL_LINKS = {
    'sdxl': 'https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0',
    'sdxl_refiner': 'https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0',
    'animatediff': 'https://huggingface.co/guoyww/animatediff',
    'svd': 'https://huggingface.co/stabilityai/stable-video-diffusion-img2vid',
    'whisper': 'https://huggingface.co/openai/whisper-large-v3'
}

def get_link(model_name):
    return MODEL_LINKS.get(model_name)
