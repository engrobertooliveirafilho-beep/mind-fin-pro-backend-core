class VideoGenerator:
    def generate(self, prompt):
        return {
            "type": "video",
            "model": "AnimateDiff/SVD",
            "output": f"video_from_{prompt}"
        }
