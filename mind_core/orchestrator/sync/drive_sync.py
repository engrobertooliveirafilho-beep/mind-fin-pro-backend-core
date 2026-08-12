class DriveSync:
    def fetch_models(self):
        return ['sdxl', 'whisper', 'svd']

    def fetch_configs(self):
        return ['k8s.yaml', 'ray.yaml']
