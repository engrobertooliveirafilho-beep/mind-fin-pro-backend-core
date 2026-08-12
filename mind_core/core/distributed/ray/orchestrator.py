class RayOrchestrator:
    def __init__(self):
        self.nodes = []

    def register_node(self, node):
        self.nodes.append(node)

    def dispatch(self, task):
        node = min(self.nodes, key=lambda x: x['load'])
        return {'node': node, 'task': task}
