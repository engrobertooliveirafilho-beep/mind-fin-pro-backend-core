class Dispatcher:
    def dispatch(self, task):
        if task['type'] in ['image','video']:
            return 'runpod_gpu'
        return 'k8s_cluster'
