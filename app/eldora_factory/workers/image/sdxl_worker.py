import redis, json, torch
from diffusers import StableDiffusionXLPipeline

r = redis.Redis(host='localhost')

pipe = StableDiffusionXLPipeline.from_pretrained(
    'stabilityai/stable-diffusion-xl-base-1.0',
    torch_dtype=torch.float16
).to('cuda')

while True:
    _, data = r.brpop('eldora_jobs')
    job = json.loads(data)

    if job['type'] == 'image':
        img = pipe(job['prompt']).images[0]
        img.save(f'outputs/{job["id"]}.png')
