class Executor:

    def route(self, task):

        if task['type'] == 'image':
            return 'runpod_sdxl'

        if task['type'] == 'video':
            return 'runpod_svd'

        if task['type'] == 'audio':
            return 'whisper_gpu'

        return 'vllm_llm'

    def execute(self, task):
        return self.route(task)
