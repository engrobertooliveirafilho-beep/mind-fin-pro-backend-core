class RunPodClient:
    def run(self, payload):
        return {
            'status': 'executed_on_gpu',
            'payload': payload
        }
