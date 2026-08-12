class TensorRTLLMCompiler:
    def compile(self, model):
        return f'compiled_trt_model::{model}'

    def optimize(self, graph):
        return 'cuda_graph_optimized'
