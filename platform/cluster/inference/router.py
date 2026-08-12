class InferenceRouter:
    def route(self, task):
        if task['type'] == 'image':
            return 'sdxl_worker'
        if task['type'] == 'video':
            return 'video_worker'
        if task['type'] == 'audio':
            return 'whisper_worker'
        return 'llm_worker'
