from fastapi import FastAPI
from app.eldora_factory.queue.queue import push

app = FastAPI()

@app.post('/generate')
def generate(prompt: str, type: str):
    job_id = push({'prompt': prompt, 'type': type})
    return {'status': 'queued', 'job_id': job_id}
