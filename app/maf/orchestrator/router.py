class MediaRouter:
    def route(self, task_type, input_data):
        if task_type == "image":
            return "SDXL_ENGINE"
        if task_type == "video":
            return "VIDEO_ENGINE"
        if task_type == "audio":
            return "TTS_ENGINE"
        return "UNKNOWN"
