class TTSEngine:
    def synthesize(self, text):
        return {
            "audio": f"tts_audio_from_{text}"
        }
