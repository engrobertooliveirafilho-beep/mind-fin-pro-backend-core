class ClusterManager:
    def scale(self, nodes, metric):
        if metric > 80:
            return 'scale_up'
        return 'stable'
