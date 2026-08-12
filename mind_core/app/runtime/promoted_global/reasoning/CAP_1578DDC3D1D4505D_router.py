class Router:
    def route(self, task):
        if task.get('type') in ['image','video']:
            return 'runpod_gpu'
        return 'vllm'
