class CUDAKernel:
    def launch(self, tensor):
        return f'cuda_kernel_executed::{tensor}'
