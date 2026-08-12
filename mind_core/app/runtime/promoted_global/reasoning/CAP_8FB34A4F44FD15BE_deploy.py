class Deployer:
    def deploy_to_runpod(self, job):
        return f'runpod_job::{job}'

    def deploy_to_k8s(self, job):
        return f'k8s_job::{job}'
