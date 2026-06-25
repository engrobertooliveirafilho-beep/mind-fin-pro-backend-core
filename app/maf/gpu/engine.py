class GPUInferenceEngine:
    def __init__(self):
        self.device = "cuda"

    def allocate(self, model_size):
        return f"allocated {model_size}GB VRAM"

    def run(self, model, input_data):
        return f"running {model} on GPU"
