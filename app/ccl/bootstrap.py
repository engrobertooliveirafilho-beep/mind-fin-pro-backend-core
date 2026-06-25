from app.ccl.agents.society import AgentSociety
from app.ccl.memory.shared_field import SharedMemoryField
from app.ccl.roles.roles import RoleSystem
from app.ccl.economy.economy import CognitiveEconomy
from app.ccl.governor.governor import CivilizationGovernor

class CognitiveCivilization:
    def __init__(self):
        self.agents = AgentSociety()
        self.memory = SharedMemoryField()
        self.roles = RoleSystem()
        self.economy = CognitiveEconomy()
        self.governor = CivilizationGovernor()

    def step(self, event):
        self.memory.write(event)
        regulation = self.governor.regulate(event)

        return {
            "memory": "updated",
            "governance": regulation
        }
