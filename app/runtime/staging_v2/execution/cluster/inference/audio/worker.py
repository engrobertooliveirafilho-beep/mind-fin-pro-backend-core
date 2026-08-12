import whisper

model = whisper.load_model('large')

def transcribe(audio):
    return model.transcribe(audio)['text']
