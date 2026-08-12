class BatchEngine:
    def group(self, requests):
        return [requests[i:i+4] for i in range(0, len(requests), 4)]
