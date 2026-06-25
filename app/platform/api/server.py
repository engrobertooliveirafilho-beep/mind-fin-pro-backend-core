from fastapi import FastAPI

app = FastAPI()

@app.post('/generate/image')
def generate_image(prompt: str):
    return {'result': f'image_from_{prompt}'}

@app.post('/generate/video')
def generate_video(prompt: str):
    return {'result': f'video_from_{prompt}'}

@app.post('/generate/audio')
def generate_audio(text: str):
    return {'result': f'audio_from_{text}'}
