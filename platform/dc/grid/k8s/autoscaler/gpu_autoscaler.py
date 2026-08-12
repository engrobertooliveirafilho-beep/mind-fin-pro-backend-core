class GPUAutoscaler:
    def scale(self, metrics):
        if metrics['gpu_util'] > 80:
            return 'scale_up'
        if metrics['gpu_util'] < 30:
            return 'scale_down'
        return 'stable'
