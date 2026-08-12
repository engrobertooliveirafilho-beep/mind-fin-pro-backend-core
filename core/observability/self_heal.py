class SelfHeal:
    def detect_failure(self, metrics):
        return metrics.get('gpu_error_rate', 0) > 0.1
