class GPUWorker:
    def run(self, job):
        return {
            'status': 'executed',
            'device': 'cuda',
            'output': f'processed_{job}'
        }
