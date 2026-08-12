from fastapi import FastAPI

app = FastAPI()

@app.post('/v1/generate')
def generate(req: dict):
    return {
        'status': 'queued',
        'model': req.get('model'),
        'type': req.get('type')
    }
