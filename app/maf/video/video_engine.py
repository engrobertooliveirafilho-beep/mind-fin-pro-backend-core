class VideoEngine:
    def generate(self, prompt):
        return {
            "model": "AnimateDiff/SVD",
            "video": f"generated_video_from_{prompt}"
        }
