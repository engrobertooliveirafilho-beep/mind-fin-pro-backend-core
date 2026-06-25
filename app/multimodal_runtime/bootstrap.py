from app.multimodal_runtime.orchestrator.orchestrator import MultimodalRuntime

class MMR:
    def __init__(self):
        self.runtime = MultimodalRuntime()

    def run(self, file_path):
        return self.runtime.process(file_path)
