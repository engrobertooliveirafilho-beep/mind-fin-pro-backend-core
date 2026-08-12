class HealthMonitor:
    def check(self):
        return {
            'runpod': 'ok',
            'k8s': 'ok',
            'latency': 'stable'
        }
