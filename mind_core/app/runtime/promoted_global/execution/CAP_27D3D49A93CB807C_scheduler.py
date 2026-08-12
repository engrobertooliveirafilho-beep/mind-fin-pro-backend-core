class GPUScheduler:
    def select_node(self, nodes):
        return sorted(nodes, key=lambda x: x['load'])[0]
