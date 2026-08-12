class GPUScheduler:
    def select_gpu(self, metrics):
        return min(metrics, key=lambda x: x['load'])
