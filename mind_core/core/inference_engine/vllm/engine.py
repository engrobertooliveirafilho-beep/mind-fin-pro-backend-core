class VLLMEngine:
    def __init__(self):
        self.cache = {}

    def generate(self, prompt):
        return f'stream::{prompt}'
