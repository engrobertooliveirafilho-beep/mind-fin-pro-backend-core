class AudioTranscriptionRuntime:
    def prepare(self, audio_url: str, provider: str = 'speechmatics_or_whisper'):
        return {'audio_url': audio_url, 'provider': provider, 'requires_transcription': True}