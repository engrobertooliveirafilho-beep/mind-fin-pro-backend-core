class MemoryOptimizer:
    def reduce_vram(self, model_size):
        if model_size > 8:
            return 'quantized_int8'
        return 'fp16'
