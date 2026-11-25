from .persistent_metrics import PersistentMetricsRegistry

class RuntimeMetrics(PersistentMetricsRegistry):
    def record_agent_turn(self, profile_key, tools_success=None, tools_fail=None):
        self.record_turn(profile_key, [] if tools_success is None else tools_success, [] if tools_fail is None else tools_fail)

    def get_agent_metrics_snapshot(self):
        return self.snapshot()

    def collect_improvement_points(self):
        return ['Persistência SQLite local; retenção e alertas não configurados.']

    def inspect_managed_agent(self, agent):
        from .agent_introspection import inspect_agent
        return inspect_agent(agent)
