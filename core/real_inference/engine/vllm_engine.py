class VLLMEngine:
    def generate(self, prompt):
        return f'vllm_stream::{prompt}'
