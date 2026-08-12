class TensorRTEngine:
    def optimize(self, model):
        return f'optimized::{model}'

    def compile(self, graph):
        return 'compiled_cuda_graph'
