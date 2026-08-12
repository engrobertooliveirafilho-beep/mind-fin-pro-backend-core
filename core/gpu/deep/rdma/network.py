class RDMANetwork:
    def send(self, src, dst, data):
        return f'rdma::{src}->{dst}::{data}'
