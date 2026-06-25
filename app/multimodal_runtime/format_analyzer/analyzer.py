class FormatAnalyzer:
    def analyze(self, file_type):
        return {
            "image": ["ocr", "vision_features"],
            "video": ["frame_extraction", "audio_track", "timeline"],
            "audio": ["transcription", "spectral_features"],
            "document": ["structure_parse", "semantic_extract"]
        }.get(file_type, [])
