class MultimodalGraphNode:
    def __init__(self, file_type, content):
        self.type = file_type
        self.content = content

    def to_graph(self):
        return {
            "node_type": self.type,
            "payload": self.content,
            "graph_ready": True
        }
