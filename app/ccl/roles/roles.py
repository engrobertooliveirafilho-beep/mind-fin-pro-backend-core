class RoleSystem:
    def assign(self, agent_type):
        roles = {
            "reasoning": "analyst",
            "memory": "archivist",
            "vision": "observer",
            "planning": "strategist",
            "critique": "auditor"
        }
        return roles.get(agent_type, "worker")
