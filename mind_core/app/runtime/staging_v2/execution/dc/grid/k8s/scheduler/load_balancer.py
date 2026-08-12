class LoadBalancer:
    def select_node(self, nodes):
        return min(nodes, key=lambda n: n['latency'])
